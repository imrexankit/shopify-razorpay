# shopify-razorpay
automates reconciliation of Sales data between Shopify and Razorpay

## Shopify-Razorpay Reconciliation Tool
### Project Overview
This project streamlines the reconciliation process between Shopify and Razorpay by providing an intuitive platform for analyzing and matching sales, orders, and payment data. Developed using Python with the Streamlit framework, the tool ensures accuracy and efficiency in financial reporting.

#### 1. Challenge/Problem
Shopify and Razorpay serve as critical tools for e-commerce operations. However, reconciling data between these platforms can be complex and error-prone due to mismatched records, refunds, and incomplete information. Businesses need a solution to automate this reconciliation, ensuring financial transparency and operational efficiency.

Key Challenges:

Handling mismatches between Shopify orders and Razorpay payments.
Managing refunds and orders efficiently.
Generating insightful visualizations and reports for better financial analysis.

#### 2. Solution/Method
Approach:
This project utilizes the following technologies and methods:

Streamlit Framework: For building an interactive, user-friendly web app.
Pandas Library: For advanced data manipulation and processing.
Matplotlib: For creating visual insights, such as pie charts and bar graphs.
Dynamic Filters: For segregating returns, orders, and combined transactions.

#### 3. Implementation
Steps:

File Upload and Processing:

Allow users to upload Shopify Sales, Orders, and Razorpay reports in Excel format.
Parse data using pandas.read_excel() and clean columns for consistency.
Data Preprocessing:

Filter and clean Shopify Orders to remove invalid rows (e.g., rows with missing subtotals).
Map Shopify orders with Razorpay payment references to identify linked transactions.
Refund and Payment Handling:

Segregate Razorpay data into credit (payments) and debit (refunds) records.
Use dynamic filtering to handle mismatched transactions efficiently.
Sales Reconciliation:

Match sales records from Shopify with Razorpay using payment references.
Create categorized reports for orders, returns, and combined transactions.
Report Generation and Visualization:

Generate grouped summaries by product type and display them in a user-friendly table.
Visualize data with pie charts, bar graphs, and histograms to provide deeper insights.

#### 4. Results
Key Benefits:

Accurate Reconciliation: Matches Shopify orders with Razorpay payments, refunds, and combined data.
Detailed Insights: Provides grouped summaries and visualizations for better understanding of sales patterns.
Interactive Platform: Allows users to dynamically filter and explore data.
Time Efficiency: Automates manual processes, reducing human errors.


#### 5. Libraries Used
Streamlit: For creating the web-based application interface.
Pandas: For robust data cleaning and manipulation.
Matplotlib: For generating pie charts, bar graphs, and histograms.
Openpyxl: For Excel file handling.

#### 6. Key Features
File Uploads: Supports uploading Shopify and Razorpay reports in .xlsx format.
Dynamic Filters: Filters transactions into orders, returns, and combined categories.
Group Summaries: Aggregates sales data by product type for quick analysis.
Interactive Visualizations: Pie charts, bar graphs, and histograms for sales trends and patterns.
This tool effectively bridges the gap between Shopify and Razorpay, offering businesses a reliable solution for sales reconciliation and financial reporting.
