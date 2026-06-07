import os
import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

def generate_ecommerce_data(num_rows: int = 50000, output_path: str = "large_dummy_data.csv"):
    print(f"Generating {num_rows} rows of e-commerce data...")
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]
    statuses = ["Completed", "Pending", "Cancelled", "Refunded"]
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Gift Card"]

    data = []
    
    start_date = datetime(2025, 1, 1)
    
    for i in range(num_rows):
        # Generate some slight irregularities to make the dataset realistic
        customer_id = fake.uuid4()
        
        # 5% chance of missing category
        category = random.choice(categories) if random.random() > 0.05 else None
        
        # Prices
        price = round(random.uniform(5.0, 1500.0), 2)
        qty = random.randint(1, 5)
        total_amount = price * qty
        
        # Discounts
        discount = round(random.uniform(0.0, 0.3) * total_amount, 2) if random.random() > 0.6 else 0.0
        final_amount = total_amount - discount
        
        # Dates
        order_date = start_date + timedelta(days=random.randint(0, 365), hours=random.randint(0, 23))
        
        row = {
            "transaction_id": f"TRX-{i+10000}",
            "customer_id": customer_id,
            "customer_email": fake.email(),
            "customer_country": fake.country(),
            "product_category": category,
            "product_name": fake.catch_phrase(),
            "unit_price": price,
            "quantity": qty,
            "discount_applied": discount,
            "final_amount": round(final_amount, 2),
            "payment_method": random.choice(payment_methods),
            "order_status": random.choice(statuses),
            "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
            "shipping_address": fake.address().replace("\n", ", ")
        }
        data.append(row)
        
        if (i + 1) % 10000 == 0:
            print(f"Generated {i + 1} rows...")

    df = pd.DataFrame(data)
    
    # Intentionally add some nulls for analysis testing
    print("Introducing some realistic null values...")
    df.loc[df.sample(frac=0.02).index, 'customer_email'] = None
    df.loc[df.sample(frac=0.01).index, 'payment_method'] = None
    
    print(f"Saving to {output_path}...")
    df.to_csv(output_path, index=False)
    print(f"Done! Dataset size: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

if __name__ == "__main__":
    generate_ecommerce_data(50000, "large_ecommerce_data.csv")
