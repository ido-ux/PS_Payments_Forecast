import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Workies Billing Tool", page_icon="💰")

st.title("💰 מחולל דוח גבייה אוטומטי - Workies")

def normalize_name(name):
    if pd.isna(name): return ""
    return str(name).replace('"', '').replace("'", "").replace("''", "").strip()

col1, col2 = st.columns(2)
with col1:
    inv_file = st.file_uploader("1. העלה קובץ חשבוניות (Excel)", type=['xlsx'])
with col2:
    cust_file = st.file_uploader("2. העלה קובץ לקוחות (CSV)", type=['csv'])

if inv_file and cust_file:
    try:
        # הפתרון לשגיאה: הוספת engine='openpyxl' וקריאה מפורשת
        df_inv = pd.read_excel(inv_file, skiprows=9, engine='openpyxl')
        df_cust = pd.read_csv(cust_file)

        df_inv['MATCH_KEY'] = df_inv['NAME'].apply(normalize_name)
        df_cust['MATCH_KEY'] = df_cust['Name'].apply(normalize_name)

        merged = pd.merge(
            df_inv, 
            df_cust[['MATCH_KEY', 'payment_method', 'Auto Charge Day']], 
            on='MATCH_KEY', 
            how='left'
        )

        # סינון - רק מה שאינו Other ואינו ריק
        final_df = merged[
            (merged['payment_method'].notna()) & 
            (merged['payment_method'] != 'Other')
        ].copy()

        # בחירת עמודות לתצוגה
        display_cols = ['DATE', 'NAME', 'OPEN BALANCE', 'payment_method', 'Auto Charge Day']
        # מוודא שהעמודות קיימות לפני תצוגה
        available_cols = [c for c in display_cols if c in final_df.columns]
        final_df = final_df[available_cols]

        st.success(f"נמצאו {len(final_df)} שורות רלוונטיות לגבייה!")
        st.dataframe(final_df, use_container_width=True)

        # הורדה לאקסל
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            final_df.to_excel(writer, index=False, sheet_name='To_Collect')
        
        st.download_button(
            label="📥 הורד דוח מעובד לאקסל",
            data=output.getvalue(),
            file_name="Workies_Billing_Report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"אירעה שגיאה בעיבוד: {e}")
