import streamlit as st
import pandas as pd
import numpy as np
import openpyxl
import matplotlib.pyplot as plt

# Streamlit app for file uploads
st.title("Shopify & Razorpay Reconciliation")

# File upload for Shopify Sales, Orders, and Razorpay reports
sales_file = st.file_uploader("Upload Shopify Sales Report (Excel)", type=["xlsx"])
orders_file = st.file_uploader("Upload Shopify Orders Report (Excel)", type=["xlsx"])
razorpay_file = st.file_uploader("Upload Razorpay Report (Excel)", type=["xlsx"])


if sales_file and orders_file and razorpay_file:
    # Read the uploaded files
    sales = pd.read_excel(sales_file)
    orders = pd.read_excel(orders_file)
    razorpay = pd.read_excel(razorpay_file)


    # Rename column names of the orders dataframe
    orders.columns = orders.columns.str.replace(' ','_').str.lower()

    # Remove rows where 'subtotal' is null
    orders = orders.dropna(subset=['subtotal'])

    # Relevant columns from orders
    orders_report = orders[['name','financial_status','subtotal', 'shipping',
        'taxes', 'total', 'discount_code', 'discount_amount','created_at','payment_reference',
        'refunded_amount', 'outstanding_balance','payment_id','payment_references']]

    # Order ID and Payment reference mapping
    order_payment_id = orders[['name','payment_reference']]
    order_payment_id['payment_reference'] = order_payment_id['payment_reference'].fillna(order_payment_id['name'])
    order_payment_id['payment_reference'] = order_payment_id['payment_reference'].str.replace(r'\.\d$','', regex=True)

    shipping_value = orders[['name', 'shipping']]

    # Razorpay Debit data (refunds)
    razorpay_debit = razorpay[(razorpay['type']=='refund') & (razorpay['settled_at']<pd.to_datetime('01-07-2024', format='%d-%m-%Y')) & 
                            ((razorpay['order_receipt'].str.startswith('#')) | (razorpay['order_receipt'].str.startswith('r')))][['order_receipt','type','settled_at', 'debit']]
    razorpay_debit.rename(columns={'type':'type_refund'},inplace=True)
    razorpay_debit['month_name'] = razorpay_debit['settled_at'].dt.strftime('%B')
    razorpay_debit = razorpay_debit.groupby(['order_receipt','type_refund', 'month_name']).agg({'debit':'sum'})

    # Razorpay Credit data (payments)
    razorpay_credit = razorpay[(razorpay['type']=='payment') & (razorpay['settled_at']<pd.to_datetime('01-07-2024', format='%d-%m-%Y')) & 
                            ((razorpay['order_receipt'].str.startswith('#')) | (razorpay['order_receipt'].str.startswith('r')))][['order_receipt','type','settled_at','amount']]
    razorpay_credit.rename(columns={'type':'type_credit'},inplace=True)
    razorpay_credit['month_name'] = razorpay_credit['settled_at'].dt.strftime('%B')
    razorpay_credit = razorpay_credit.groupby(['order_receipt','type_credit','month_name']).agg({'amount':'sum'})

    # Merging Razorpay credit and debit data
    rzr_final = razorpay_credit.merge(razorpay_debit, on=['order_receipt','month_name'], how='outer', suffixes=(['_credit', '_debit'])).fillna(0)

    # Sales Calculation
    rzr_final['sales'] = rzr_final['amount'] - rzr_final['debit']
    rzr_sales = rzr_final.groupby('order_receipt').agg({'amount':'sum', 'debit':'sum', 'sales':'sum'}).reset_index()

    # Merging with order payment data
    new_rzr = rzr_sales.merge(order_payment_id, left_on='order_receipt', right_on='payment_reference', validate='one_to_one')

    # Matching sales with Razorpay data
    salesMatchRzr = sales[(sales['order_name'].isin(new_rzr['payment_reference'])) | (sales['order_name'].isin(new_rzr['name']))]

    # Filter returns
    only_returns_filter = new_rzr[(new_rzr['debit']>0) & (new_rzr['amount']==0)][['order_receipt','name', 'sales']]
    sales_return_filtered = salesMatchRzr[(salesMatchRzr['order_name'].isin(only_returns_filter['order_receipt'])) | (salesMatchRzr['order_name'].isin(only_returns_filter['name']))]
    sales_return_filtered = sales_return_filtered[sales_return_filtered['sale_kind']=='return'].drop(['sale_kind','day'], axis=1)

    # Filter orders
    only_order_filter = new_rzr[(new_rzr['amount']>0) & (new_rzr['debit']==0)][['order_receipt','name', 'sales']]
    sales_order_filtered = salesMatchRzr[(salesMatchRzr['order_name'].isin(only_order_filter['order_receipt'])) | (salesMatchRzr['order_name'].isin(only_order_filter['name']))]
    sales_order_filtered = sales_order_filtered[sales_order_filtered['sale_kind']=='order'].drop('day', axis=1)

    # Handling both return and order
    both_filtered = new_rzr[(new_rzr['amount']>0) & (new_rzr['debit']>0)][['order_receipt','name','sales']]
    order_return_filter = salesMatchRzr[(salesMatchRzr['order_name'].isin(both_filtered['order_receipt'])) | (salesMatchRzr['order_name'].isin(both_filtered['name']))].drop('day', axis=1)

    # Process shipping data for returns and orders
    shipping_value = shipping_value.rename(columns={'name':'order_name', 'shipping':'total_sales'})
    shipping_value['product_type']="Shipping"
    shipping_value['units_per_transaction']=0
    shipping_value = shipping_value[['order_name', 'product_type', 'total_sales', 'units_per_transaction']]

    # Final processing for returns and orders
    shipping_for_returns = shipping_value[shipping_value['order_name'].isin(sales_return_filtered['order_name'])].reset_index()
    shipping_for_orders = shipping_value[shipping_value['order_name'].isin(sales_order_filtered['order_name'])].reset_index()

    # Grouping for final table
    final_table = pd.concat([sales_order_filtered, sales_return_filtered, shipping_for_returns, shipping_for_orders], ignore_index=True)
    final_table.loc[:,'product_type'] = final_table['product_type'].fillna(final_table['product_type'].value_counts().idxmax())

    grouped_table = final_table.groupby('product_type').agg({'total_sales':'sum'})
    #print(grouped_table)


    # Display the resulting table
    st.write("Grouped Product-Type Wise Summary:")
    with st.expander("Click to view larger table"):
        st.dataframe(grouped_table, height=600)  # Adjust height for larger table
#    st.dataframe(grouped_table)



    # Sort and get top 5 products
    top_5_products = final_table.groupby('product_type')['total_sales'].sum().nlargest(5)

    # Create a pie chart top 5 products
    fig, ax = plt.subplots(facecolor='#0e1117')
    ax.pie(top_5_products, labels=top_5_products.index, autopct='%1.1f%%', 
           startangle=90,textprops={'color': 'white'})
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Display bar chart in Streamlit
    st.pyplot(fig)


    # Group by product_type to get total sales for each type
    sales_by_product_type = final_table.groupby('product_type')['total_sales'].sum()

    # Create a bar chart
    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(sales_by_product_type.index, sales_by_product_type.values)

    # Set labels and title
    ax_bar.set_xlabel('Product Type')
    ax_bar.set_ylabel('Total Sales')
    ax_bar.set_title('Total Sales by Product Type')

    # Rotate product names for better readability
    plt.xticks(rotation=45)


    # Display chart in Streamlit
    st.pyplot(fig_bar)



    # Create a histogram of the total sales values
    fig_hist, ax_hist = plt.subplots()
    ax_hist.hist(final_table['total_sales'], bins=20, color='purple')

    # Set labels and title
    ax_hist.set_xlabel('Sales Amount')
    ax_hist.set_ylabel('Frequency')
    ax_hist.set_title('Distribution of Total Sales')

    # Display histogram in Streamlit
    st.pyplot(fig_hist)




else:
    st.write("Please upload all three files to proceed.")