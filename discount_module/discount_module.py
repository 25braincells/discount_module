import json
from utils import setup_logging, log_info, log_error, format_currency

# Discount calculation functions
def apply_fixed_amount_discount(cart_total, amount):
    return max(cart_total - amount, 0)

def apply_percentage_discount(cart_total, percentage):
    return cart_total * (1 - percentage / 100)

def apply_percentage_discount_by_category(cart_items, category, percentage):
    category_total = sum(item['price'] for item in cart_items if item['category'] == category)
    discount_amount = category_total * percentage / 100
    return category_total - discount_amount

def apply_discount_by_points(cart_total, points):
    max_discount = cart_total * 0.2  # Maximum discount is capped at 20% of cart total
    discount_amount = min(points, max_discount)
    return cart_total - discount_amount

def apply_special_campaign_discount(cart_total, x_thb, y_thb):
    discount_amount = (cart_total // x_thb) * y_thb
    return discount_amount

# Calculate final price function
def calculate_final_price(cart_items, discount_campaigns):
    cart_total = sum(item['price'] for item in cart_items)
    
    # Apply discounts in the order: Coupon > On Top > Seasonal
    applied_coupon = False
    applied_on_top = False
    applied_seasonal = False
    
    for campaign in discount_campaigns:
        category = campaign['category']
        campaign_type = campaign['type']

        if category == 'Coupon' and not applied_coupon:
            if campaign_type == 'Fixed amount':
                amount = campaign['amount']
                cart_total = apply_fixed_amount_discount(cart_total, amount)
            elif campaign_type == 'Percentage discount':
                percentage = campaign['percentage']
                cart_total = apply_percentage_discount(cart_total, percentage)
            applied_coupon = True
        
        elif category == 'On Top' and not applied_on_top:
            if campaign_type == 'Percentage discount by item category':
                item_category = campaign['parameters']['category']
                percentage = campaign['parameters']['Percentage']
                cart_total = apply_percentage_discount_by_category(cart_items, item_category, percentage)
            elif campaign_type == 'Discount by points':
                points = campaign['parameters']['Customer points']
                cart_total = apply_discount_by_points(cart_total, points)
            applied_on_top = True
        
        elif category == 'Seasonal' and not applied_seasonal:
            if campaign_type == 'Special campaigns':
                x_thb = campaign['parameters']['Every X THB']
                y_thb = campaign['parameters']['Discount Y THB']
                cart_total -= apply_special_campaign_discount(cart_total, x_thb, y_thb)
            applied_seasonal = True
    
    return cart_total

# Main function
def main():
    setup_logging()

    # Read cart items from JSON file
    cart_items_path = 'discount_module/data/cart_items.json'
    try:
        with open(cart_items_path, 'r') as f:
            cart_items = json.load(f)
    except FileNotFoundError:
        log_error(f"Error: Cart items file '{cart_items_path}' not found.")
        return
    except json.JSONDecodeError:
        log_error(f"Error: Failed to decode JSON from '{cart_items_path}'.")
        return
    
    log_info("Cart items loaded successfully.")

    # Read discount campaigns from JSON file
    discount_campaigns_path = 'discount_module/data/discount_campaigns.json'
    try:
        with open(discount_campaigns_path, 'r') as f:
            discount_campaigns = json.load(f)
    except FileNotFoundError:
        log_error(f"Error: Discount campaigns file '{discount_campaigns_path}' not found.")
        return
    except json.JSONDecodeError:
        log_error(f"Error: Failed to decode JSON from '{discount_campaigns_path}'.")
        return
    
    log_info("Discount campaigns loaded successfully.")

    # Calculate final price after applying discounts
    final_price = calculate_final_price(cart_items, discount_campaigns)

    # Display the final price formatted as THB
    log_info(f"Final price after applying discounts: {format_currency(final_price)}")

if __name__ == "__main__":
    main()
