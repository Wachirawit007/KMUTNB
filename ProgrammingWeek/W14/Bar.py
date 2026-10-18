import matplotlib.pyplot as plt

products = ['Product A', 'Product B', 'Product C']
revenue = [45000, 78000, 32000]

plt.bar(products, revenue,
        color=['#1f77b4', '#ff7f0e', '#2ca02c'])
plt.ylabel('Revenue ($)')
plt.title('Product Performance')
plt.show()
