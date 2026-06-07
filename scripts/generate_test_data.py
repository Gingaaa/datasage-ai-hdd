import pandas as pd
from faker import Faker
import random

def generate_small_test_data(num_rows=1000, output_path="chart_testing_data.csv"):
    fake = Faker()
    Faker.seed(42)
    random.seed(42)

    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys"]
    statuses = ["Completed", "Pending", "Cancelled", "Refunded"]
    payment_methods = ["Credit Card", "PayPal", "Bank Transfer", "Gift Card"]
    
    data = []
    for i in range(num_rows):
        data.append({
            "transaction_id": f"TRX-{i+1000}",
            "customer_country": fake.country(),
            "product_category": random.choice(categories),
            "payment_method": random.choice(payment_methods),
            "order_status": random.choice(statuses),
            "unit_price": round(random.uniform(5.0, 500.0), 2)
        })
        
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Saved {num_rows} rows to {output_path}")

if __name__ == "__main__":
    generate_small_test_data()
