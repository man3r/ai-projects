# 🍽️ AI-Powered Food Ordering Store

A complete food ordering system with AI chat assistant, built for home-based food businesses.

## ✨ Features

### Customer Experience
- 🤖 **AI Chat Ordering** - Natural language ordering with Ollama
- 🛍️ **Product Browsing** - Instagram-style product cards with category filters
- 🛒 **Smart Cart** - Real-time updates, persists across sessions
- 📦 **Order Tracking** - Domino's-style visual progress tracker
- 📱 **Mobile Optimized** - Responsive design for all devices

### Business Owner
- 📊 **Dashboard** - Today's stats, revenue, pending orders
- 🏪 **Product Management** - Add, edit, delete products
- 📋 **Order Management** - Update status, view details
- 👥 **Customer Analytics** - Track orders, spending patterns

### Technical
- ⚡ **Fast API** - Built with FastAPI + SQLAlchemy
- 🧠 **Local AI** - Ollama integration (no API costs)
- 🎨 **Modern UI** - Clean, professional design
- 💾 **SQLite** - Simple, portable database
- 🔒 **Privacy First** - All data stays on your server

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Ollama with llama3.2 model
- SQLite

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd ollama-python/web-ui

# Install dependencies
pip install -r requirements.txt

# Initialize database
python init_db.py

# Create demo data
python -c "from utils.demo_data import create_demo_store; from database.db import get_db_session; create_demo_store(get_db_session(), 1)"

# Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### First Visit

```bash
# Storefront (Customer)
http://localhost:8000/store/ammas-kitchen

# Dashboard (Admin - requires login)
http://localhost:8000/
```

---

## 📂 Project Structure

```
web-ui/
├── app.py                      # Main FastAPI application
├── database/
│   ├── models.py              # SQLAlchemy models (8 tables)
│   ├── crud_store.py          # Store CRUD operations
│   ├── db.py                  # Database configuration
│   └── crud.py                # Existing CRUD operations
├── utils/
│   ├── demo_data.py           # Demo store generator
│   └── ai_helpers.py          # AI chat & suggestions
├── templates/
│   ├── storefront/
│   │   ├── store.html         # Main storefront
│   │   ├── cart.html          # Cart & checkout
│   │   └── track.html         # Order tracking
│   └── index.html             # Admin dashboard
└── static/
    ├── css/
    ├── js/
    └── uploads/
```

---

## 🗄️ Database Schema

### Core Models
- **Business** - Store information, settings
- **StoreCategory** - Product categories (Batters, Flours, etc.)
- **StoreProduct** - Products with pricing, inventory
- **StoreCustomer** - Customer profiles, addresses
- **StoreOrder** - Orders with status tracking
- **StoreOrderItem** - Individual order items
- **StoreChatMessage** - AI chat history

---

## 🎯 API Endpoints

### Customer Facing
```
GET  /store/{slug}                    # Storefront home
GET  /store/{slug}/products           # List products
POST /store/{slug}/chat               # AI chat
POST /store/{slug}/orders             # Place order
GET  /store/{slug}/orders/{number}    # Track order
```

### Admin (Authenticated)
```
GET  /api/store/dashboard             # Overview stats
GET  /api/store/products              # List products
POST /api/store/products              # Create product
PUT  /api/store/products/{id}         # Update product
GET  /api/store/orders                # List orders
PUT  /api/store/orders/{id}/status    # Update status
```

---

## 🤖 AI Features

### Conversational Ordering
```
Customer: "breakfast for 2"
AI: "Here are our breakfast items:"
[Shows IDLI/DOSA Batter + Wheat Flakes]

Customer: "add 2 batters"
AI: "Added 2 IDLI/DOSA Batters to your cart."
```

### Smart Suggestions
- Context-aware product recommendations
- Complementary item suggestions
- Quantity adjustments based on conversation

### Powered by Ollama
- Uses llama3.2:latest locally
- No API costs
- Privacy-first (data stays local)
- Fast response times

---

## 📱 Demo Store

**Amma's Kitchen** - Included demo data:
- 8 Products across 4 categories
- 2 Sample customers
- 3 Sample orders (various statuses)

Products:
- 🥞 Batters (IDLI/DOSA, Special IDLI)
- 🌾 Flours (Rice, Wheat)
- 🫘 Flakes (Wheat, Rice)
- 🍿 Snacks (Murukku Mix)

---

## 🎨 Design Principles

- **Mobile First** - Optimized for phone ordering
- **Instagram Vibes** - Modern, clean product cards
- **Fast & Simple** - 3-step checkout (< 30 seconds)
- **Visual Feedback** - Animations, progress indicators
- **No Dependencies** - Pure HTML/CSS/JS for frontend

---

## 🔧 Configuration

### Business Settings
Edit in database or via admin panel:
- Delivery fee
- Free delivery threshold
- Minimum order value
- Store open/closed status

### AI Behavior
Customize in `utils/ai_helpers.py`:
- Response tone (formal/casual)
- Product suggestions logic
- Conversation prompts

---

## 📊 Order Status Flow

```
pending → confirmed → preparing → ready → delivered
```

Each status updates timestamps automatically.

---

## 🧪 Testing

### Test Storefront
```bash
# Visit storefront
open http://localhost:8000/store/ammas-kitchen

# Test AI chat
Type: "breakfast" or "2 batters and flour"

# Test checkout
Add items → Cart → Fill details → Place order
```

### Test with Mobile
```bash
# Terminal 1: Run server
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Expose with ngrok
ngrok http 8000

# Share ngrok URL via WhatsApp
```

---

## 🚀 Production Deployment

### Environment Variables
```bash
DATABASE_URL=sqlite:///./store.db
OLLAMA_HOST=http://localhost:11434
SECRET_KEY=your-secret-key-here
```

### Recommended Stack
- **Server**: AWS EC2, DigitalOcean, Linode
- **Database**: PostgreSQL (upgrade from SQLite)
- **Web Server**: Nginx + Uvicorn
- **SSL**: Let's Encrypt (Certbot)

---

## 🛣️ Roadmap

### Phase 1 ✅ (Complete)
- [x] Customer storefront
- [x] AI chat ordering
- [x] Cart & checkout
- [x] Order tracking
- [x] Basic admin API

### Phase 2 🚧 (In Progress)
- [ ] Admin panel UI
- [ ] Product image upload
- [ ] Order management dashboard
- [ ] Customer analytics

### Phase 3 📋 (Planned)
- [ ] Payment integration (Razorpay)
- [ ] WhatsApp notifications
- [ ] SMS order updates
- [ ] Multi-business support
- [ ] Inventory management

---

## 🤝 Contributing

This is a personal project. Feel free to fork and customize for your needs!

---

## 📄 License

MIT License - Use freely for personal or commercial projects

---

## 🙏 Acknowledgments

- Built with FastAPI, SQLAlchemy, Ollama
- Inspired by Domino's tracker, Instagram Shopping
- Designed for home-based food entrepreneurs

---

## 📞 Support

For issues or questions, create an issue in the repository.

---

**Built with ❤️ for home food businesses**
