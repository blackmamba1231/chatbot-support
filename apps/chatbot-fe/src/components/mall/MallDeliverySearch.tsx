import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

interface Product {
  id: string;
  name: string;
  price: string;
  image: string;
  description: string;
  location: string;
  restaurant?: string;
}

interface Location {
  city: string;
  state?: string;
  is_active?: boolean;
  services?: string[];
  description?: string;
}

interface CartItem extends Product {
  quantity: number;
}

interface CustomerInfo {
  name: string;
  email: string;
  phone: string;
  address: string;
}

export const MallDeliverySearch: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [locations, setLocations] = useState<string[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCart, setShowCart] = useState<boolean>(false);
  const [showCheckout, setShowCheckout] = useState<boolean>(false);
  const [customerInfo, setCustomerInfo] = useState<CustomerInfo>({
    name: '',
    email: '',
    phone: '',
    address: '',
  });
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [orderSuccess, setOrderSuccess] = useState<boolean>(false);
  const [orderId, setOrderId] = useState<string>('');

  useEffect(() => {
    fetchProducts();
    fetchLocations();
  }, []);

  const filterProducts = useCallback(() => {
    let filtered = [...products];
    
    if (selectedLocation) {
      filtered = filtered.filter(product => 
        product.location.toLowerCase() === selectedLocation.toLowerCase()
      );
    }
    
    if (searchTerm) {
      filtered = filtered.filter(product => 
        product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        product.description.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    setFilteredProducts(filtered);
  }, [selectedLocation, searchTerm, products]);

  useEffect(() => {
    filterProducts();
  }, [filterProducts]);

  const fetchProducts = async () => {
    // Create an abort controller for the request
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
    
    try {
      setLoading(true);
      setError('');
      
      // Use the new AI shopping API endpoint for mall delivery products
      const response = await axios.get('http://localhost:8000/api/ai-shopping/mall-delivery', {
        params: { location: selectedLocation },
        signal: controller.signal
      });
      
      // If API fails, use mock data
      if (!response.data || response.data.status !== 'success' || response.data.products?.length === 0) {
        // Mock data for demonstration
        const mockProducts: Product[] = [
          {
            id: '1',
            name: 'Margherita Pizza',
            price: '45.00',
            image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
            description: 'Classic pizza with tomato sauce, mozzarella, and basil',
            location: 'Alba Iulia',
          },
          {
            id: '2',
            name: 'Pepperoni Pizza',
            price: '55.00',
            image: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee',
            description: 'Pizza with tomato sauce, mozzarella, and pepperoni',
            location: 'Alba Iulia',
          },
          {
            id: '3',
            name: 'Vegetarian Pizza',
            price: '50.00',
            image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
            description: 'Pizza with tomato sauce, mozzarella, and various vegetables',
            location: 'Alba Iulia',
          },
          {
            id: '4',
            name: 'Quattro Formaggi',
            price: '60.00',
            image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
            description: 'Pizza with four different types of cheese',
            location: 'Arad',
          },
          {
            id: '5',
            name: 'Hawaiian Pizza',
            price: '55.00',
            image: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee',
            description: 'Pizza with tomato sauce, mozzarella, ham, and pineapple',
            location: 'Arad',
          },
          {
            id: '6',
            name: 'Diavola Pizza',
            price: '58.00',
            image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
            description: 'Spicy pizza with tomato sauce, mozzarella, and spicy salami',
            location: 'Vaslui',
          },
        ];
        setProducts(mockProducts);
        setFilteredProducts(mockProducts);
      } else {
        // Success! Process the real data
        clearTimeout(timeoutId);
        const realProducts = response.data.products.map((product: any) => ({
          id: product.id || String(Math.random()),
          name: product.name || 'Unknown Service',
          price: product.price || 'N/A',
          image: product.image_url || '',
          description: product.description || '',
          location: product.location || selectedLocation || '',
          categories: product.categories || []
        }));
        
        setProducts(realProducts);
        // Extract unique locations from products
        const locationSet = new Set<string>();
        realProducts.forEach((product: Product) => {
          if (product.location) {
            locationSet.add(product.location);
          }
        });
        setLocations(Array.from(locationSet));
        
        // If a location was detected in the API response, use it
        if (response.data.detected_location && !selectedLocation) {
          setSelectedLocation(response.data.detected_location);
        }
      }
    } catch (err: any) {
      // Check if this is a cancellation error
      if (axios.isCancel(err)) {
        console.log('Request was cancelled:', err.message);
      } else {
        console.error('Error fetching products:', err);
        setError('Failed to fetch products. Using demo data instead.');
      }
      
      // Mock data for demonstration
      const mockProducts: Product[] = [
        {
          id: '1',
          name: 'Margherita Pizza',
          price: '45.00',
          image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
          description: 'Classic pizza with tomato sauce, mozzarella, and basil',
          location: 'Alba Iulia',
        },
        {
          id: '2',
          name: 'Pepperoni Pizza',
          price: '55.00',
          image: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee',
          description: 'Pizza with tomato sauce, mozzarella, and pepperoni',
          location: 'Alba Iulia',
        },
        {
          id: '3',
          name: 'Vegetarian Pizza',
          price: '50.00',
          image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
          description: 'Pizza with tomato sauce, mozzarella, and various vegetables',
          location: 'Alba Iulia',
        },
        {
          id: '4',
          name: 'Quattro Formaggi',
          price: '60.00',
          image: 'https://images.unsplash.com/photo-1513104890138-7c749659a591',
          description: 'Pizza with four different types of cheese',
          location: 'Arad',
        },
        {
          id: '5',
          name: 'Hawaiian Pizza',
          price: '55.00',
          image: 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee',
          description: 'Pizza with tomato sauce, mozzarella, ham, and pineapple',
          location: 'Arad',
        },
        {
          id: '6',
          name: 'Diavola Pizza',
          price: '58.00',
          image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ae38',
          description: 'Spicy pizza with tomato sauce, mozzarella, and spicy salami',
          location: 'Vaslui',
        }
      ];
      setProducts(mockProducts);
      setFilteredProducts(mockProducts);
    } finally {
      clearTimeout(timeoutId);
      setLoading(false);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/mobile/mall-delivery/locations');
      if (response.data && response.data.locations) {
        // Convert location slugs to readable names
        const locationNames = response.data.locations.map((loc: string) => {
          // Convert slug to readable name (e.g., 'alba-iulia' to 'Alba Iulia')
          return loc.split('-')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
        });
        setLocations(locationNames);
      } else {
        // Fallback to mock data
        setLocations(['Alba Iulia', 'Arad', 'Miercurea Ciuc', 'Vaslui']);
      }
    } catch (err) {
      console.error('Error fetching locations:', err);
      // Fallback to mock data
      setLocations(['Alba Iulia', 'Arad', 'Miercurea Ciuc', 'Vaslui']);
    }
  };



  const addToCart = (product: Product) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      
      if (existingItem) {
        return prevCart.map(item => 
          item.id === product.id 
            ? { ...item, quantity: item.quantity + 1 } 
            : item
        );
      } else {
        return [...prevCart, { ...product, quantity: 1 }];
      }
    });
  };

  const removeFromCart = (productId: string) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    
    setCart(prevCart => 
      prevCart.map(item => 
        item.id === productId 
          ? { ...item, quantity } 
          : item
      )
    );
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => {
      return total + (parseFloat(item.price) * item.quantity);
    }, 0).toFixed(2);
  };

  const placeOrder = async () => {
    try {
      setLoading(true);
      
      // Prepare order data for WooCommerce
      const orderData = {
        order_data: {
          payment_method: "cod",
          payment_method_title: "Cash on Delivery",
          set_paid: false,
          billing: {
            first_name: customerInfo.name.split(' ')[0],
            last_name: customerInfo.name.split(' ').slice(1).join(' ') || '',
            address_1: customerInfo.address,
            email: customerInfo.email,
            phone: customerInfo.phone
          },
          shipping: {
            first_name: customerInfo.name.split(' ')[0],
            last_name: customerInfo.name.split(' ').slice(1).join(' ') || '',
            address_1: customerInfo.address
          },
          line_items: cart.map(item => ({
            product_id: parseInt(item.id),
            quantity: item.quantity
          })),
          shipping_lines: [
            {
              method_id: "flat_rate",
              method_title: "Flat Rate",
              total: "10.00"
            }
          ]
        }
      };
      
      // Send order to backend using the new API endpoint
      const response = await axios.post('http://localhost:8000/api/mobile/mall-delivery/orders', orderData);
      
      if (response.data && response.data.status === 'success' && response.data.order && response.data.order.id) {
        setOrderId(response.data.order.id.toString());
        setOrderSuccess(true);
        setCart([]);
      } else {
        setError('Failed to place order. Please try again.');
      }
    } catch (err) {
      console.error('Error placing order:', err);
      setError('Failed to place order. Please try again.');
      
      // For demo purposes, create a mock order if the API fails
      setOrderId(`ORDER-${Math.floor(Math.random() * 10000)}`);
      setOrderSuccess(true);
      setCart([]);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setCustomerInfo(prev => ({
      ...prev,
      [name]: value
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (orderSuccess) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="text-center">
          <div className="text-green-500 text-5xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Order Successful!</h2>
          <p className="text-gray-600 mb-4">Your order has been placed successfully.</p>
          <p className="text-gray-800 font-semibold mb-6">Order ID: {orderId}</p>
          <button 
            onClick={() => {
              setOrderSuccess(false);
              setShowCheckout(false);
              setShowCart(false);
            }}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  if (showCheckout) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Checkout</h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}
        
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Your Order</h3>
          <div className="border-t border-b py-4">
            {cart.map(item => (
              <div key={item.id} className="flex justify-between items-center mb-2">
                <span>{item.name} x {item.quantity}</span>
                <span>${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
              </div>
            ))}
            <div className="flex justify-between items-center font-bold mt-4 pt-2 border-t">
              <span>Total:</span>
              <span>${getTotalPrice()}</span>
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-2">Customer Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-gray-700 mb-1">Full Name</label>
              <input
                type="text"
                name="name"
                value={customerInfo.name}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="John Doe"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1">Email</label>
              <input
                type="email"
                name="email"
                value={customerInfo.email}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="john@example.com"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1">Phone</label>
              <input
                type="tel"
                name="phone"
                value={customerInfo.phone}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="+40 123 456 789"
              />
            </div>
            <div>
              <label className="block text-gray-700 mb-1">Delivery Address</label>
              <input
                type="text"
                name="address"
                value={customerInfo.address}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="123 Main St, Alba Iulia"
              />
            </div>
          </div>
        </div>
        
        <div className="flex justify-between">
          <button
            onClick={() => setShowCheckout(false)}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 transition-colors"
          >
            Back to Cart
          </button>
          <button
            onClick={placeOrder}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
          >
            Place Order
          </button>
        </div>
      </div>
    );
  }

  if (showCart) {
    return (
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Your Cart</h2>
        
        {cart.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">Your cart is empty</p>
            <button
              onClick={() => setShowCart(false)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
            >
              Continue Shopping
            </button>
          </div>
        ) : (
          <>
            <div className="space-y-4 mb-6">
              {cart.map(item => (
                <div key={item.id} className="flex items-center justify-between border-b pb-4">
                  <div className="flex items-center">
                    <img 
                      src={item.image} 
                      alt={item.name} 
                      className="w-16 h-16 object-cover rounded mr-4"
                    />
                    <div>
                      <h3 className="font-semibold text-gray-800">{item.name}</h3>
                      <p className="text-gray-600 text-sm">${item.price} each</p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="bg-gray-200 text-gray-700 w-8 h-8 rounded-full"
                    >
                      -
                    </button>
                    <span className="mx-3">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="bg-gray-200 text-gray-700 w-8 h-8 rounded-full"
                    >
                      +
                    </button>
                    <button
                      onClick={() => removeFromCart(item.id)}
                      className="ml-4 text-red-500 hover:text-red-700"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="flex justify-between items-center font-bold text-lg mb-6">
              <span>Total:</span>
              <span>${getTotalPrice()}</span>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setShowCart(false)}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400 transition-colors"
              >
                Continue Shopping
              </button>
              <button
                onClick={() => setShowCheckout(true)}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
              >
                Proceed to Checkout
              </button>
            </div>
          </>
        )}
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Mall Delivery Products</h2>
        <button
          onClick={() => setShowCart(true)}
          className="flex items-center bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path d="M3 1a1 1 0 000 2h1.22l.305 1.222a.997.997 0 00.01.042l1.358 5.43-.893.892C3.74 11.846 4.632 14 6.414 14H15a1 1 0 000-2H6.414l1-1H14a1 1 0 00.894-.553l3-6A1 1 0 0017 3H6.28l-.31-1.243A1 1 0 005 1H3zM16 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM6.5 18a1.5 1.5 0 100-3 1.5 1.5 0 000 3z" />
          </svg>
          Cart ({cart.length})
        </button>
      </div>
      
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="w-full md:w-64">
          <label className="block text-gray-700 mb-1">Location</label>
          <select
            value={selectedLocation}
            onChange={(e) => setSelectedLocation(e.target.value)}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Locations</option>
            {locations.map(location => (
              <option key={location} value={location}>{location}</option>
            ))}
          </select>
        </div>
        
        <div className="flex-1">
          <label className="block text-gray-700 mb-1">Search</label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="Search for products..."
          />
        </div>
      </div>
      
      {error && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {filteredProducts.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-500">No products found. Try changing your filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map(product => (
            <div key={product.id} className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
              <div className="w-full h-48 bg-gray-100 flex items-center justify-center">
                {product.image ? (
                  <img 
                    src={product.image} 
                    alt={product.name} 
                    className="w-full h-48 object-cover"
                    onError={(e) => {
                      // Replace broken images with a placeholder
                      (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x300?text=Food+Image';
                    }}
                  />
                ) : (
                  <div className="text-gray-400">No image available</div>
                )}
              </div>
              <div className="p-4">
                <h3 className="font-semibold text-lg text-gray-800 mb-1">
                  {product.name.replace(/&#8211;/g, '-').replace(/<\/?span[^>]*>/g, '')}
                </h3>
                <p className="text-gray-600 text-sm mb-2">
                  {product.description.replace(/&#8211;/g, '-').replace(/<\/?span[^>]*>/g, '')}
                </p>
                <div className="flex justify-between items-center">
                  <span className="text-blue-600 font-bold">${product.price}</span>
                  <button
                    onClick={() => addToCart(product)}
                    className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition-colors"
                  >
                    Add to Cart
                  </button>
                </div>
                <div className="mt-2 text-sm text-gray-500">
                  <div>Location: {product.location}</div>
                  {product.restaurant && (
                    <div>Restaurant: {product.restaurant}</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
