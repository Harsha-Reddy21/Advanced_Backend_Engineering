# Zomato v3 - Complete Food Delivery System

## Overview
A comprehensive food delivery API built with FastAPI, implementing complex multi-table relationships and advanced business logic. This version includes customer management, order processing with status workflow, review system, and analytics.

## 🚀 Features

### Core Entities
- **Restaurants**: Full CRUD with operating hours, ratings, and locations
- **Menu Items**: Items with categories, dietary information, and availability
- **Customers**: User management with contact information and order history  
- **Orders**: Complex order processing with status workflow and item tracking
- **Reviews**: Rating system tied to completed orders

### Advanced Functionality
- **Order Status Workflow**: `placed` → `confirmed` → `preparing` → `out_for_delivery` → `delivered` → `cancelled`
- **Business Logic Validation**: Operating hours, review eligibility, status transitions
- **Analytics**: Customer spending patterns, restaurant performance metrics
- **Advanced Search**: Multi-filter restaurant and order search
- **Real-time Calculations**: Order totals, delivery estimates, rating updates

## 🏗️ Database Schema

### Relationships
- **One-to-Many**: Customer → Orders, Restaurant → Orders, Restaurant → Menu Items
- **Many-to-Many with Association**: Order ↔ Menu Items (via Order Items with quantity/price)
- **Complex Joins**: Reviews linking Customers, Restaurants, and Orders

### Key Tables
- `customers`: User information and preferences
- `restaurants`: Restaurant details and operational data
- `menu_items`: Items with pricing and dietary information
- `orders`: Order headers with status and delivery info
- `order_items`: Association table with quantity and pricing at time of order
- `reviews`: Rating and feedback system

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI 
- **Database**: SQLite with async support (aiosqlite)
- **ORM**: SQLAlchemy with async capabilities
- **Validation**: Pydantic schemas with comprehensive validation
- **Authentication**: Email validation and phone number formatting

## 📚 API Endpoints

### Customers (`/customers`)
- `POST /customers/` - Create customer
- `GET /customers/` - List customers with pagination
- `GET /customers/{id}` - Get customer details
- `PUT /customers/{id}` - Update customer
- `DELETE /customers/{id}` - Delete customer
- `GET /customers/{id}/orders` - Customer order history
- `POST /customers/{id}/orders` - Place new order
- `GET /customers/{id}/reviews` - Customer reviews
- `GET /customers/{id}/analytics` - Customer analytics

### Orders (`/orders`)
- `GET /orders/{id}` - Get order with full details
- `PUT /orders/{id}/status` - Update order status
- `GET /orders/` - List orders with filters (restaurant, customer, status, date range)
- `POST /orders/{id}/review` - Add review for completed order
- `GET /orders/{id}/can-review` - Check review eligibility

### Reviews (`/reviews`)
- `GET /reviews/restaurants/{id}` - Restaurant reviews
- `GET /reviews/restaurants/{id}/summary` - Review statistics
- `GET /reviews/customers/{id}` - Customer reviews
- `GET /reviews/{id}` - Detailed review information

### Restaurants (`/restaurants`)
- **Enhanced with analytics**:
- `GET /restaurants/search/advanced` - Multi-filter search
- `GET /restaurants/{id}/orders` - Restaurant orders
- `GET /restaurants/{id}/analytics` - Performance metrics
- `GET /restaurants/{id}/reviews` - Restaurant reviews

### Menu Items (`/menu-items`)
- All existing CRUD operations
- Enhanced with order integration

## 🔧 Installation & Setup

1. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run Application**:
```bash
uvicorn main:app --reload
```

3. **Access Documentation**:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Business Logic

### Order Processing
1. **Validation**: Menu item availability, restaurant hours, customer existence
2. **Calculation**: Total amount based on current prices, estimated delivery time
3. **Status Management**: Enforced workflow with validation
4. **Item Tracking**: Preserve pricing at time of order

### Review System  
1. **Eligibility**: Only delivered orders can be reviewed
2. **Ownership**: Customers can only review their own orders
3. **Rating Updates**: Automatic restaurant rating recalculation
4. **Duplicate Prevention**: One review per order

### Analytics
1. **Restaurant Metrics**: Total orders, revenue, popular items, status distribution
2. **Customer Insights**: Spending patterns, favorite restaurants, order frequency
3. **Performance Tracking**: Real-time calculations and historical data

## 🧪 Example Usage

### Place an Order
```python
# 1. Create customer
customer_data = {
    "name": "John Doe",
    "email": "john@example.com", 
    "phone_number": "+1234567890",
    "address": "123 Main St, City"
}

# 2. Place order
order_data = {
    "restaurant_id": 1,
    "delivery_address": "123 Main St, City",
    "order_items": [
        {"menu_item_id": 1, "quantity": 2},
        {"menu_item_id": 3, "quantity": 1, "special_requests": "Extra spicy"}
    ]
}

# 3. Track order status progression
# placed → confirmed → preparing → out_for_delivery → delivered
```

### Add Review
```python
# Only after order is delivered
review_data = {
    "rating": 5,
    "comment": "Excellent food and fast delivery!"
}
```

## 🔍 Advanced Features

### Search & Filtering
- **Restaurant Search**: By cuisine, location, rating, active status
- **Order Filtering**: By date range, status, customer, restaurant
- **Menu Filtering**: By category, dietary preferences

### Analytics Dashboard
- **Restaurant Performance**: Revenue trends, popular items, order volume
- **Customer Behavior**: Spending analysis, ordering patterns, preferences
- **System Metrics**: Order status distribution, average ratings

### Business Rules
- **Operating Hours**: Enforce restaurant availability
- **Status Workflow**: Prevent invalid status transitions  
- **Review Integrity**: Validate review eligibility
- **Price Consistency**: Lock prices at order time

## 🚦 Status Codes & Error Handling

- **200**: Successful operation
- **201**: Resource created successfully
- **204**: Resource deleted successfully
- **400**: Bad request (validation errors, business rule violations)
- **403**: Forbidden (ownership violations)
- **404**: Resource not found
- **422**: Validation error

## 📈 Performance Considerations

- **Database Indexing**: Strategic indexes on foreign keys and search fields
- **Eager Loading**: Optimized joins for complex relationships
- **Pagination**: Consistent pagination across all list endpoints
- **Caching**: Schema-level optimizations for repeated calculations

## 🔮 Future Enhancements

- **Authentication & Authorization**: User roles and permissions
- **Payment Integration**: Payment processing and tracking
- **Real-time Updates**: WebSocket connections for order tracking
- **Recommendation Engine**: AI-powered menu suggestions
- **Delivery Tracking**: GPS integration and real-time location updates
- **Multi-tenant Support**: Restaurant chain management

---

**Version**: 3.0.0  
**Author**: Zomato Development Team  
**License**: MIT
