import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="HR Analytics Dashboard",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define the color palette
color_palette = {
    'light_gray': '#F1F1F1',
    'dark_gray': '#202020',
    'gray_blue': '#7E909A',
    'dark_blue': '#1C4E80',
    'light_blue': '#A5D8DD',
    'orange': '#EA6A47',
    'vivid_blue': '#0091D5',
    'neutral_light_gray': '#F0F0F0',
    'neutral_dark_gray': '#333333'
}

# Custom CSS to improve the look and feel with the new color palette
st.markdown(f"""
    <style>
    .main {{
        padding: 0rem 1rem;
        background-color: {color_palette['light_gray']};
    }}
    .stMetric {{
        background-color: {color_palette['light_gray']};
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    div[data-testid="stMetricValue"] {{
        font-size: 28px;
        color: {color_palette['dark_gray']};
    }}
    div[data-testid="stMetricDelta"] {{
        font-size: 16px;
    }}
    </style>
""", unsafe_allow_html=True)

# Load data function
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('HR_Analytics.csv')
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Main title with emoji
st.title("👥 HR Analytics Dashboard")
st.markdown("---")

# Load the data
df = load_data()

if df is not None:
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Department filter
    departments = st.sidebar.multiselect(
        "Select Departments",
        options=sorted(df['Department'].unique()),
        default=sorted(df['Department'].unique())
    )
    
    # Job Role filter
    roles = st.sidebar.multiselect(
        "Select Job Roles",
        options=sorted(df['JobRole'].unique()),
        default=sorted(df['JobRole'].unique())
    )
    
    # Gender filter
    gender_filter = st.sidebar.multiselect(
        "Select Gender",
        options=sorted(df['Gender'].unique()),
        default=sorted(df['Gender'].unique())
    )
    
    # Experience filter
    exp_range = st.sidebar.slider(
        "Years of Experience",
        min_value=int(df['TotalWorkingYears'].min()),
        max_value=int(df['TotalWorkingYears'].max()),
        value=(int(df['TotalWorkingYears'].min()), int(df['TotalWorkingYears'].max()))
    )
    
    # Filter the dataframe
    filtered_df = df[
        (df['Department'].isin(departments)) &
        (df['JobRole'].isin(roles)) &
        (df['Gender'].isin(gender_filter)) &
        (df['TotalWorkingYears'].between(exp_range[0], exp_range[1]))
    ]
    
    # Store the filtered data in session state for consistency across tabs
    st.session_state.filtered_df = filtered_df
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        "💼 Workforce Demographics",
        "💰 Compensation",
        "😊 Employee Satisfaction"
    ])
    
    # Tab 1: Overview
    with tab1:
        # Key Metrics Row
        st.subheader("Key Insights")
        col1, col2, col3 = st.columns(3)
        
        # Calculate metrics
        attrition_rate = (st.session_state.filtered_df['Attrition'].value_counts(normalize=True).get('Yes', 0) * 100)
        avg_satisfaction = st.session_state.filtered_df['JobSatisfaction'].mean()
        avg_salary = st.session_state.filtered_df['MonthlyIncome'].mean()
        
        with col1:
            st.metric(
                "Overall Attrition Rate",
                f"{attrition_rate:.1f}%",
                delta=f"{attrition_rate - df['Attrition'].value_counts(normalize=True).get('Yes', 0) * 100:.1f}%",
                delta_color="inverse"
            )
        
        with col2:
            st.metric(
                "Average Job Satisfaction",
                f"{avg_satisfaction:.2f}/4",
                delta=f"{avg_satisfaction - df['JobSatisfaction'].mean():.2f}",
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Average Monthly Income",
                f"${avg_salary:,.0f}",
                delta=f"${avg_salary - df['MonthlyIncome'].mean():,.0f}",
                delta_color="normal"
            )
        
        st.markdown("---")
       
        
        # Overview Charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Department Distribution
            dept_dist = px.pie(
                st.session_state.filtered_df,
                names='Department',
                title='Employee Distribution by Department',
                hole=0.4,
                color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
                labels={'Department': 'Department'},
                hover_data=['Department'],
                template='plotly_white'
            )
            st.plotly_chart(dept_dist, use_container_width=True)
        
        with col2:
            # Attrition by Department
            dept_attrition = st.session_state.filtered_df.groupby('Department')['Attrition'].apply(
                lambda x: (x == 'Yes').mean() * 100
            ).reset_index()
            
            attrition_chart = px.bar(
                dept_attrition,
                x='Department',
                y='Attrition',
                title='Attrition Rate by Department',
                color='Department',
                text=dept_attrition['Attrition'].round(1),
                labels={'Attrition': 'Attrition Rate (%)'},
                color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
                template='plotly_white'
            )
            attrition_chart.update_traces(texttemplate='%{text}%', textposition='outside')
            attrition_chart.update_layout(
                annotations=[
                    dict(
                        x="Sales",
                        y=dept_attrition[dept_attrition['Department'] == 'Sales']['Attrition'].values[0],
                        text="Highest Attrition",
                        showarrow=True,
                        arrowhead=1,
                        ax=0,
                        ay=-40
                    )
                ]
            )
            st.plotly_chart(attrition_chart, use_container_width=True)
    
    # Tab 2: Workforce Demographics
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Age Distribution
            age_dist = px.histogram(
                st.session_state.filtered_df,
                x='Age',
                title='Age Distribution',
                nbins=30,
                color='Gender',
                labels={'Age': 'Age', 'count': 'Count'},
                color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue']],
                template='plotly_white'
            )
            st.plotly_chart(age_dist, use_container_width=True)
        
        with col2:
            # Education Field Distribution
            edu_dist = px.pie(
                st.session_state.filtered_df,
                names='EducationField',
                title='Distribution by Education Field',
                color_discrete_sequence=[color_palette['light_blue'], color_palette['orange'], color_palette['gray_blue']],
                labels={'EducationField': 'Education Field'},
                hover_data=['EducationField'],
                template='plotly_white'
            )
            st.plotly_chart(edu_dist, use_container_width=True)
        
        # Experience vs Performance
        exp_perf = px.scatter(
            st.session_state.filtered_df,
            x='TotalWorkingYears',
            y='PerformanceRating',
            color='Department',
            size='MonthlyIncome',
            title='Experience vs Performance Rating',
            trendline="ols",
            labels={'TotalWorkingYears': 'Total Working Years', 'PerformanceRating': 'Performance Rating'},
            color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
            template='plotly_white'
        )
        st.plotly_chart(exp_perf, use_container_width=True)
    
    # Tab 3: Compensation
    with tab3:
        st.subheader("Salary Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Salary by Job Role
            salary_role = st.session_state.filtered_df.groupby('JobRole')['MonthlyIncome'].mean().reset_index()
            salary_chart = px.bar(
                salary_role,
                x='JobRole',
                y='MonthlyIncome',
                title='Average Salary by Job Role',
                color='JobRole',
                labels={'MonthlyIncome': 'Monthly Income', 'JobRole': 'Job Role'},
                color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
                template='plotly_white'
            )
            salary_chart.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(salary_chart, use_container_width=True)
        
        with col2:
            # Salary Distribution
            salary_dist = px.box(
                st.session_state.filtered_df,
                x='Department',
                y='MonthlyIncome',
                title='Salary Distribution by Department',
                color='Department',
                labels={'MonthlyIncome': 'Monthly Income', 'Department': 'Department'},
                color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
                template='plotly_white'
            )
            st.plotly_chart(salary_dist, use_container_width=True)
        
        # Detailed Salary Table
        st.subheader("Detailed Salary Breakdown")
        salary_stats = st.session_state.filtered_df.groupby('JobRole').agg({
            'MonthlyIncome': ['mean', 'min', 'max', 'std'],
            'PercentSalaryHike': 'mean'
        }).round(2)
        salary_stats.columns = ['Avg Salary', 'Min Salary', 'Max Salary', 'Std Dev', 'Avg % Hike']
        st.dataframe(salary_stats, use_container_width=True)
        
        # Recommendations
        
    
    # Tab 4: Employee Satisfaction
    with tab4:
        col1, col2 = st.columns(2)
        
        with col1:
            # Satisfaction Heatmap
            satisfaction_data = pd.crosstab(
                st.session_state.filtered_df['JobSatisfaction'],
                st.session_state.filtered_df['WorkLifeBalance']
            )
            
            fig_heatmap = px.imshow(
                satisfaction_data,
                title='Job Satisfaction vs Work-Life Balance',
                labels=dict(x='Work Life Balance', y='Job Satisfaction', color='Count'),
                color_continuous_scale='Viridis',
                template='plotly_white'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        
        with col2:
            # Average Satisfaction Metrics
            satisfaction_metrics = ['JobSatisfaction', 'EnvironmentSatisfaction', 
                                 'RelationshipSatisfaction', 'WorkLifeBalance']
            avg_satisfaction = st.session_state.filtered_df[satisfaction_metrics].mean()
            
            radar_fig = go.Figure(data=go.Scatterpolar(
                r=avg_satisfaction.values,
                theta=avg_satisfaction.index,
                fill='toself'
            ))
            radar_fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 4])),
                showlegend=False,
                title='Average Satisfaction Metrics',
                template='plotly_white'
            )
            st.plotly_chart(radar_fig, use_container_width=True)
        
        # Satisfaction by Department
        env_sat = st.session_state.filtered_df.groupby('Department')[satisfaction_metrics].mean().reset_index()
        env_sat_long = pd.melt(
            env_sat,
            id_vars=['Department'],
            value_vars=satisfaction_metrics,
            var_name='Metric',
            value_name='Score'
        )
        
        satisfaction_by_dept = px.bar(
            env_sat_long,
            x='Department',
            y='Score',
            color='Metric',
            title='Satisfaction Metrics by Department',
            barmode='group',
            labels={'Score': 'Satisfaction Score', 'Department': 'Department'},
            color_discrete_sequence=[color_palette['dark_blue'], color_palette['vivid_blue'], color_palette['light_blue']],
            template='plotly_white'
        )
        st.plotly_chart(satisfaction_by_dept, use_container_width=True)

    # Footer
    st.markdown("---")
    st.markdown(f"*Dashboard last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*")
else:
    st.error("Unable to load the HR Analytics dataset. Please check the file path and try again.")
