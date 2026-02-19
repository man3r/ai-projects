def generate_primes(limit):
    primes = []
    for num in range(2, limit + 1):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def main():
    limit = int(input("Enter the limit number: "))
    prime_numbers = generate_primes(limit)
    print(f"Prime numbers up to {limit}: {prime_numbers}")

if __name__ == "__main__":
    main()