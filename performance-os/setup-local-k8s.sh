#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Performance OS: Local Kubernetes Setup ===${NC}"

# 1. Install Nginx Ingress Controller
echo -e "${YELLOW}Installing Nginx Ingress Controller...${NC}"
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml

# 2. Install Argo CD
echo -e "\n${YELLOW}Installing Argo CD...${NC}"
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts

# Expose Argo CD UI via NodePort
echo -e "\n${YELLOW}Exposing Argo CD UI...${NC}"
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "NodePort"}}'

# Wait for Argo CD server to be ready before getting password
echo -e "\n${YELLOW}Waiting for Argo CD to start (this takes about 1 minute)...${NC}"
kubectl rollout status deployment/argocd-server -n argocd

# 3. Configure GitHub Access
echo -e "\n${BLUE}=== GitHub Authentication ===${NC}"
echo "Argo CD needs a GitHub Personal Access Token (PAT) with 'repo' scope to read the private repository."
read -p "Enter your GitHub PAT (input will be hidden): " -s GITHUB_PAT
echo ""

if [ -z "$GITHUB_PAT" ]; then
    echo "No PAT provided. Argo CD will not be able to sync private repositories."
else
    echo -e "${YELLOW}Configuring private repository access in Argo CD...${NC}"
    kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: private-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
stringData:
  type: git
  url: https://github.com/man3r/ai-projects.git
  password: $GITHUB_PAT
  username: man3r
EOF
    echo -e "${GREEN}GitHub PAT configured successfully.${NC}"
fi

# 4. Deploy Performance OS Application via Argo CD
echo -e "\n${YELLOW}Deploying Performance OS Application configuration...${NC}"
# Check if we are in the ai-projects directory or performance-os directory
if [ -f "k8s/06-argocd-app.yaml" ]; then
    kubectl apply -f k8s/06-argocd-app.yaml
elif [ -f "performance-os/k8s/06-argocd-app.yaml" ]; then
    kubectl apply -f performance-os/k8s/06-argocd-app.yaml
else
    echo "Warning: Could not find k8s/06-argocd-app.yaml. Are you running this from the right directory?"
fi

# 5. Get Credentials and Wrap Up
echo -e "\n${BLUE}=== Setup Complete! ===${NC}"
echo -e "Waiting for initial admin password generation..."
sleep 2

PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d 2>/dev/null || echo "Password not ready yet. Run 'kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath=\"{.data.password}\" | base64 -d' in a few seconds.")

echo -e "\n${GREEN}Argo CD is available at:${NC} https://localhost:8080"
echo -e "${GREEN}Username:${NC} admin"
echo -e "${GREEN}Password:${NC} $PASSWORD"
echo -e "\nTo access the UI, run this command in a separate terminal:"
echo -e "${YELLOW}kubectl port-forward svc/argocd-server -n argocd 8080:443${NC}"
echo -e "\nOnce logged in, hit 'Refresh' on the performance-os app to trigger the first sync!"
