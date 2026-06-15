import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

# Page configuration
st.set_page_config(
    page_title="BhashaDaan Analytics Dashboard",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center; }
    .sub-header { font-size: 1.5rem; font-weight: bold; color: #2c3e50; margin-top: 20px; }
    .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   padding: 20px; border-radius: 15px; color: white; }
    .insight-box { background-color: #f8f9fa; padding: 15px; border-left: 4px solid #1f77b4;
                   border-radius: 5px; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"> BhashaDaan Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("📁 Data Upload")
    
    # Load sheets directly
    user_reg_df = pd.read_excel(r"C:\Users\sneha\Downloads\BHASHHINI\BhashaDaan_Data.xlsx", sheet_name="User Registerations")
    contrib_df = pd.read_excel(r"C:\Users\sneha\Downloads\BHASHHINI\BhashaDaan_Data.xlsx", sheet_name="Contribution Counts")
    
    # Convert date columns
    user_reg_df['Activity_date'] = pd.to_datetime(user_reg_df['Activity_date'], format='%m/%d/%Y')
    contrib_df['Activity_date'] = pd.to_datetime(contrib_df['Activity_date'], format='%m/%d/%Y')
    
    # Create month-year columns
    user_reg_df['Month_Year'] = user_reg_df['Activity_date'].dt.strftime('%B %Y')
    user_reg_df['Month_Num'] = user_reg_df['Activity_date'].dt.to_period('M')
    
    contrib_df['Month_Year'] = contrib_df['Activity_date'].dt.strftime('%B %Y')
    contrib_df['Month_Num'] = contrib_df['Activity_date'].dt.to_period('M')
    
    # Sort by date
    user_reg_df = user_reg_df.sort_values('Activity_date')
    contrib_df = contrib_df.sort_values('Activity_date')
    
    st.info(f"📊 User Registration: {len(user_reg_df)} records")
    st.info(f"📊 Contribution Counts: {len(contrib_df)} records")

# Main content
# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 User Registration Analysis",
    "🌍 Language Contribution Analysis", 
    "🔗 User-Contributor Analysis",
    "📊 Advanced Insights",
    "🎯 Recommendations"
])

# ==================== TAB 1: USER REGISTRATION ANALYSIS ====================
with tab1:
    st.markdown('<div class="sub-header">📈 User Registration Trends</div>', unsafe_allow_html=True)
    
    # Monthly aggregation for user registration
    monthly_users = user_reg_df.groupby('Month_Year').agg({
        'New_users': 'sum',
        'Contributors': 'sum',
        'Activity_date': 'first'
    }).reset_index()
    
    # Sort by date
    monthly_users['sort_date'] = pd.to_datetime(monthly_users['Activity_date'])
    monthly_users = monthly_users.sort_values('sort_date')
    
    # Display monthly line chart
    st.subheader("Monthly User Registration & Contributors Trend")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly_users['Month_Year'],
        y=monthly_users['New_users'],
        mode='lines+markers',
        name='New Users',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    fig.add_trace(go.Scatter(
        x=monthly_users['Month_Year'],
        y=monthly_users['Contributors'],
        mode='lines+markers',
        name='Contributors',
        line=dict(color='green', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Monthly New Users vs Contributors",
        xaxis_title="Month",
        yaxis_title="Count",
        hovermode='x unified',
        height=500,
        xaxis_tickangle=-45
    )
    
    
    # Add click interaction
    fig.update_traces(hovertemplate='<b>%{x}</b><br>Count: %{y:,.0f}<extra></extra>')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly drill-down selector
    st.subheader("🔍 Drill Down to Daily Data")
    selected_month = st.selectbox(
        "Select a month to see daily breakdown",
        monthly_users['Month_Year'].tolist()
    )
    
    if selected_month:
        # Filter data for selected month
        month_data = user_reg_df[user_reg_df['Month_Year'] == selected_month]
        
        # Create daily chart
        fig_daily = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Daily New Users', 'Daily Contributors'),
            vertical_spacing=0.15
        )
        
        fig_daily.add_trace(
            go.Bar(x=month_data['Activity_date'], y=month_data['New_users'], 
                   name='New Users', marker_color='blue'),
            row=1, col=1
        )
        
        fig_daily.add_trace(
            go.Bar(x=month_data['Activity_date'], y=month_data['Contributors'], 
                   name='Contributors', marker_color='green'),
            row=2, col=1
        )
        
        fig_daily.update_layout(height=600, showlegend=False,
                                title_text=f"Daily Breakdown for {selected_month}")
        fig_daily.update_xaxes(title_text="Date", row=2, col=1)
        
        st.plotly_chart(fig_daily, use_container_width=True)
        
        # Show daily data table
        with st.expander("📋 View Daily Data Table"):
            st.dataframe(month_data, use_container_width=True)

# ==================== TAB 2: LANGUAGE CONTRIBUTION ANALYSIS ====================
with tab2:
    st.markdown('<div class="sub-header">🌍 Language-wise Contribution Analysis</div>', unsafe_allow_html=True)
    
    # Monthly language contribution
    monthly_lang = contrib_df.groupby(['Month_Year', 'Language']).agg({
        'Contributions': 'sum',
        'Validations': 'sum'
    }).reset_index()
    
    # Get unique months for selection
    months_list = sorted(contrib_df['Month_Year'].unique())
    
    # Month selector for language analysis
    selected_lang_month = st.selectbox("Select Month for Language Analysis", months_list, key="lang_month")
    
    if selected_lang_month:
        month_lang_data = monthly_lang[monthly_lang['Month_Year'] == selected_lang_month]
        
        # Two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Contributions by language
            fig_contrib = px.bar(month_lang_data, 
                                x='Language', y='Contributions',
                                title=f'Contributions by Language - {selected_lang_month}',
                                color='Contributions',
                                color_continuous_scale='Viridis')
            fig_contrib.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_contrib, use_container_width=True)
        
        with col2:
            # Validations by language
            fig_valid = px.bar(month_lang_data,
                              x='Language', y='Validations',
                              title=f'Validations by Language - {selected_lang_month}',
                              color='Validations',
                              color_continuous_scale='Plasma')
            fig_valid.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_valid, use_container_width=True)
        
        # Language-wise drill down to daily
        st.subheader(f"📅 Daily Breakdown for {selected_lang_month}")
        
        # Get all languages for the selected month
        languages = month_lang_data['Language'].tolist()
        selected_lang = st.selectbox("Select Language to see daily trend", languages)
        
        if selected_lang:
            # Filter daily data for selected language and month
            daily_lang = contrib_df[
                (contrib_df['Month_Year'] == selected_lang_month) & 
                (contrib_df['Language'] == selected_lang)
            ]
            
            # Daily trend
            fig_daily_lang = make_subplots(
                rows=2, cols=1,
                subplot_titles=(f'Daily Contributions - {selected_lang}', 
                               f'Daily Validations - {selected_lang}')
            )
            
            fig_daily_lang.add_trace(
                go.Scatter(x=daily_lang['Activity_date'], y=daily_lang['Contributions'],
                          mode='lines+markers', name='Contributions',
                          line=dict(color='orange', width=2)),
                row=1, col=1
            )
            
            fig_daily_lang.add_trace(
                go.Scatter(x=daily_lang['Activity_date'], y=daily_lang['Validations'],
                          mode='lines+markers', name='Validations',
                          line=dict(color='red', width=2)),
                row=2, col=1
            )
            
            fig_daily_lang.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig_daily_lang, use_container_width=True)
            
            # Show daily data
            with st.expander(f"📋 Daily Data for {selected_lang} - {selected_lang_month}"):
                st.dataframe(daily_lang, use_container_width=True)
    
    # Top languages overall
    st.subheader("🏆 Top Performing Languages (All Time)")
    top_languages = contrib_df.groupby('Language').agg({
        'Contributions': 'sum',
        'Validations': 'sum'
    }).sort_values('Contributions', ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    with col1:
        fig_top_contrib = px.bar(top_languages, x=top_languages.index, y='Contributions',
                                 title='Top 10 Languages by Contributions',
                                 color='Contributions')
        st.plotly_chart(fig_top_contrib, use_container_width=True)
    
    with col2:
        fig_top_valid = px.bar(top_languages, x=top_languages.index, y='Validations',
                               title='Top 10 Languages by Validations',
                               color='Validations')
        st.plotly_chart(fig_top_valid, use_container_width=True)

# ==================== TAB 3: USER-CONTRIBUTOR ANALYSIS ====================
with tab3:
    st.markdown('<div class="sub-header">🔗 User to Contributor Conversion Analysis</div>', unsafe_allow_html=True)
    
    # Calculate conversion metrics
    user_reg_df['Contributor_Rate'] = (user_reg_df['Contributors'] / user_reg_df['New_users'] * 100).round(2)
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_users = user_reg_df['New_users'].sum()
        st.metric("Total New Users", f"{total_users:,}")
    
    with col2:
        total_contributors = user_reg_df['Contributors'].sum()
        st.metric("Total Contributors", f"{total_contributors:,}")
    
    with col3:
        overall_rate = (total_contributors / total_users * 100) if total_users > 0 else 0
        st.metric("Overall Conversion Rate", f"{overall_rate:.1f}%")
    
    with col4:
        avg_daily_users = user_reg_df['New_users'].mean()
        st.metric("Avg Daily New Users", f"{avg_daily_users:.0f}")
    
    # Monthly conversion rate trend
    st.subheader("📈 Monthly Contributor Conversion Rate")
    
    monthly_conversion = user_reg_df.groupby('Month_Year').agg({
        'New_users': 'sum',
        'Contributors': 'sum'
    }).reset_index()
    
    monthly_conversion['Conversion_Rate'] = (monthly_conversion['Contributors'] / monthly_conversion['New_users'] * 100).round(2)
    
    fig_conversion = px.line(monthly_conversion, x='Month_Year', y='Conversion_Rate',
                             markers=True, text='Conversion_Rate',
                             title="Monthly Contributor Conversion Rate Trend")
    fig_conversion.update_traces(textposition='top center')
    fig_conversion.update_layout(yaxis_title="Conversion Rate (%)", height=400)
    st.plotly_chart(fig_conversion, use_container_width=True)
    
    # Identify patterns
    st.subheader("🎯 When do users become contributors?")
    
    # Create contributor efficiency metric
    user_reg_df['Contributor_Efficiency'] = (user_reg_df['Contributors'] / user_reg_df['New_users'] * 100).fillna(0)
    
    # Best and worst months
    best_month = monthly_conversion.loc[monthly_conversion['Conversion_Rate'].idxmax()]
    worst_month = monthly_conversion.loc[monthly_conversion['Conversion_Rate'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"**🏆 Best Converting Month:**\n\n{best_month['Month_Year']}\nConversion Rate: {best_month['Conversion_Rate']:.1f}%\nNew Users: {best_month['New_users']:,}\nContributors: {best_month['Contributors']:,}")
    
    with col2:
        st.warning(f"**⚠️ Lowest Converting Month:**\n\n{worst_month['Month_Year']}\nConversion Rate: {worst_month['Conversion_Rate']:.1f}%\nNew Users: {worst_month['New_users']:,}\nContributors: {worst_month['Contributors']:,}")
    
    # Correlation analysis
    st.subheader("📊 Correlation: New Users vs Contributors")
    
    # Calculate correlation
    correlation = user_reg_df['New_users'].corr(user_reg_df['Contributors'])
    
    fig_scatter = px.scatter(user_reg_df, x='New_users', y='Contributors',
                             title=f'New Users vs Contributors (Correlation: {correlation:.3f})',
                             trendline="ols",
                             labels={'New_users': 'New Users', 'Contributors': 'Contributors'},
                             color='Month_Year')
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    if correlation > 0.7:
        st.success(f"✅ Strong positive correlation ({correlation:.3f}) - More users naturally lead to more contributors")
    elif correlation > 0.3:
        st.info(f"📈 Moderate correlation ({correlation:.3f}) - Other factors influence contributor conversion")
    else:
        st.warning(f"⚠️ Weak correlation ({correlation:.3f}) - Focus on conversion strategies rather than just user acquisition")

# ==================== TAB 4: ADVANCED INSIGHTS ====================
with tab4:
    st.markdown('<div class="sub-header">📊 Advanced Analytics & Insights</div>', unsafe_allow_html=True)
    
    # Insight 1: Contribution to Validation Ratio
    st.subheader("💡 Contribution Quality Analysis")
    
    contrib_df['Contribution_Quality'] = (contrib_df['Validations'] / contrib_df['Contributions'] * 100).round(2)
    
    # Language quality ranking
    lang_quality = contrib_df.groupby('Language').agg({
        'Contributions': 'sum',
        'Validations': 'sum'
    }).reset_index()
    lang_quality['Validation_Rate'] = (lang_quality['Validations'] / lang_quality['Contributions'] * 100).round(2)
    lang_quality = lang_quality.sort_values('Validation_Rate', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_quality = px.bar(lang_quality.head(10), x='Language', y='Validation_Rate',
                            title='Top 10 Languages by Validation Rate (Quality)',
                            color='Validation_Rate',
                            color_continuous_scale='Greens')
        fig_quality.update_layout(height=400)
        st.plotly_chart(fig_quality, use_container_width=True)
    
    with col2:
        # Languages needing improvement
        low_quality = lang_quality[lang_quality['Validation_Rate'] < 50].head(10)
        if len(low_quality) > 0:
            fig_low = px.bar(low_quality, x='Language', y='Validation_Rate',
                            title='Languages Needing Quality Improvement (<50% Validation)',
                            color='Validation_Rate',
                            color_continuous_scale='Reds')
            fig_low.update_layout(height=400)
            st.plotly_chart(fig_low, use_container_width=True)
        else:
            st.success("🎉 All languages have >50% validation rate!")
    
    # Insight 2: User Activity Patterns
    st.subheader("📅 User Activity Patterns")
    
    # Add weekday analysis
    user_reg_df['Weekday'] = user_reg_df['Activity_date'].dt.day_name()
    weekday_activity = user_reg_df.groupby('Weekday')[['New_users', 'Contributors']].mean().reset_index()
    
    # Order weekdays
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_activity['Weekday'] = pd.Categorical(weekday_activity['Weekday'], categories=weekday_order, ordered=True)
    weekday_activity = weekday_activity.sort_values('Weekday')
    
    fig_weekday = go.Figure()
    fig_weekday.add_trace(go.Bar(x=weekday_activity['Weekday'], y=weekday_activity['New_users'],
                                 name='Avg New Users', marker_color='blue'))
    fig_weekday.add_trace(go.Bar(x=weekday_activity['Weekday'], y=weekday_activity['Contributors'],
                                 name='Avg Contributors', marker_color='green'))
    fig_weekday.update_layout(title="Average Daily Activity by Weekday",
                              xaxis_title="Day of Week",
                              yaxis_title="Average Count",
                              barmode='group',
                              height=400)
    st.plotly_chart(fig_weekday, use_container_width=True)
    
    # Find best day for engagement
    best_day = weekday_activity.loc[weekday_activity['Contributors'].idxmax(), 'Weekday']
    st.info(f"💡 **Insight:** {best_day} has the highest contributor activity. Consider running campaigns or challenges on this day!")
    
    # Insight 3: Growth Trends
    st.subheader("📈 Growth Trend Analysis")
    
    # Calculate month-over-month growth
    monthly_growth = monthly_conversion.copy()
    monthly_growth['User_Growth'] = monthly_growth['New_users'].pct_change() * 100
    monthly_growth['Contributor_Growth'] = monthly_growth['Contributors'].pct_change() * 100
    
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=monthly_growth['Month_Year'], y=monthly_growth['User_Growth'],
                                    mode='lines+markers', name='User Growth %',
                                    line=dict(color='blue', width=2)))
    fig_growth.add_trace(go.Scatter(x=monthly_growth['Month_Year'], y=monthly_growth['Contributor_Growth'],
                                    mode='lines+markers', name='Contributor Growth %',
                                    line=dict(color='green', width=2)))
    fig_growth.add_hline(y=0, line_dash="dash", line_color="red")
    fig_growth.update_layout(title="Month-over-Month Growth Rate",
                             xaxis_title="Month",
                             yaxis_title="Growth Rate (%)",
                             height=400)
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Insight 4: Language Contribution Heatmap
    st.subheader("🌍 Language Contribution Heatmap Over Time")
    
    # Create pivot table for heatmap
    heatmap_data = contrib_df.groupby(['Month_Year', 'Language'])['Contributions'].sum().unstack()
    
    # Select top 10 languages for heatmap
    top_langs = contrib_df.groupby('Language')['Contributions'].sum().nlargest(10).index
    heatmap_top = heatmap_data[top_langs]
    
    fig_heatmap = px.imshow(heatmap_top.T, 
                            title="Language Contribution Heatmap (Top 10 Languages)",
                            labels=dict(x="Month", y="Language", color="Contributions"),
                            aspect="auto",
                            color_continuous_scale='Viridis')
    fig_heatmap.update_layout(height=500)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ==================== TAB 5: RECOMMENDATIONS ====================
with tab5:
    st.markdown('<div class="sub-header">🎯 Actionable Recommendations</div>', unsafe_allow_html=True)
    
    # Calculate key metrics for recommendations
    overall_conversion = (user_reg_df['Contributors'].sum() / user_reg_df['New_users'].sum() * 100)
    
    # Find languages with high contribution but low validation
    lang_quality_analysis = contrib_df.groupby('Language').agg({
        'Contributions': 'sum',
        'Validations': 'sum'
    }).reset_index()
    lang_quality_analysis['Validation_Rate'] = (lang_quality_analysis['Validations'] / lang_quality_analysis['Contributions'] * 100)
    
    high_contrib_low_quality = lang_quality_analysis[
        (lang_quality_analysis['Contributions'] > lang_quality_analysis['Contributions'].quantile(0.75)) &
        (lang_quality_analysis['Validation_Rate'] < 50)
    ]
    
    # Find best performing months
    best_months = monthly_conversion.nlargest(3, 'Conversion_Rate')
    
    # Display recommendations
    st.markdown("### Based on your data analysis, here are key recommendations:")
    
    # Recommendation 1: Conversion Improvement
    with st.expander("📈 **Improve User to Contributor Conversion**", expanded=True):
        if overall_conversion < 30:
            st.warning(f"⚠️ Current conversion rate is {overall_conversion:.1f}%, which is below optimal levels")
            st.markdown("""
            **Action Items:**
            1. **Onboarding Tutorial:** Add a guided tutorial for new users showing how to contribute
            2. **Gamification:** Introduce badges for first contribution
            3. **Welcome Email:** Send personalized welcome email with quick contribution tips
            4. **Easy First Task:** Suggest simple contributions (e.g., validating existing content)
            """)
        else:
            st.success(f"✅ Good conversion rate at {overall_conversion:.1f}%")
            st.markdown("""
            **Maintain and Enhance:**
            1. **Reward Consistent Contributors:** Implement a loyalty program
            2. **Community Features:** Add leaderboards and community challenges
            3. **Feedback Loop:** Ask contributors for suggestions to improve platform
            """)
    
    # Recommendation 2: Language Quality Focus
    with st.expander("🌍 **Language Quality Improvement**", expanded=True):
        if len(high_contrib_low_quality) > 0:
            st.warning(f"⚠️ {len(high_contrib_low_quality)} languages have high contributions but low validation rates")
            st.markdown(f"**Focus Languages:** {', '.join(high_contrib_low_quality['Language'].head(5).tolist())}")
            st.markdown("""
            **Action Items:**
            1. **Review Process:** Implement peer review system for these languages
            2. **Quality Guidelines:** Provide clear quality guidelines and examples
            3. **Expert Review:** Assign language experts to review contributions
            4. **Validation Incentives:** Reward validators with points/badges
            """)
        else:
            st.success("✅ All languages maintaining good quality standards!")
    
    # Recommendation 3: Best Practices from Top Months
    with st.expander("📅 **Learn from Best Performing Months**", expanded=True):
        st.markdown(f"**Top Performing Month:** {best_months.iloc[0]['Month_Year']} with {best_months.iloc[0]['Conversion_Rate']:.1f}% conversion")
        st.markdown("""
        **What worked well:**
        1. High user engagement strategies
        2. Effective onboarding during that period
        3. Community-driven initiatives
        
        **Action Items:**
        - Analyze specific campaigns/activities during top months
        - Replicate successful strategies
        - Document best practices for future reference
        """)
    
    # Recommendation 4: Timing Optimization
    with st.expander("⏰ **Optimal Timing for Engagement**", expanded=True):
        best_weekday = weekday_activity.loc[weekday_activity['Contributors'].idxmax(), 'Weekday']
        st.markdown(f"""
        **Key Findings:**
        - **Best day for contributor activity:** {best_weekday}
        - **Peak user registration days:** {weekday_activity.nlargest(3, 'New_users')['Weekday'].tolist()}
        
        **Action Items:**
        1. **Schedule Campaigns:** Launch new initiatives on {best_weekday}
        2. **Email Newsletters:** Send on day before peak activity
        3. **Community Events:** Host virtual meetups on high-activity days
        4. **Push Notifications:** Schedule reminders on optimal days
        """)
    
    # Recommendation 5: Language Strategy
    with st.expander("🎯 **Language Contribution Strategy**", expanded=True):
        top_languages_list = top_languages.head(5).index.tolist()
        bottom_languages = top_languages.tail(5).index.tolist()
        
        st.markdown(f"""
        **Top Performing Languages:** {', '.join(top_languages_list)}
        **Languages Needing Growth:** {', '.join(bottom_languages)}
        
        **Action Items for Top Languages:**
        1. **Advanced Features:** Add language-specific advanced features
        2. **Community Ambassadors:** Recruit ambassadors from top language communities
        3. **Content Challenges:** Run language-specific contribution challenges
        
        **Action Items for Growing Languages:**
        1. **Targeted Outreach:** Focus marketing on these language communities
        2. **Simplified Tools:** Provide easier contribution tools for these languages
        3. **Incentive Programs:** Offer bonuses for contributions in underrepresented languages
        """)
    
    # Export recommendations
    st.markdown("---")
    st.markdown("### 📋 Download Analysis Report")
    
    # Create summary dataframe
    summary_data = {
        'Metric': ['Total New Users', 'Total Contributors', 'Overall Conversion Rate', 
                  'Number of Languages', 'Total Contributions', 'Total Validations'],
        'Value': [
            f"{user_reg_df['New_users'].sum():,}",
            f"{user_reg_df['Contributors'].sum():,}",
            f"{overall_conversion:.1f}%",
            len(contrib_df['Language'].unique()),
            f"{contrib_df['Contributions'].sum():,}",
            f"{contrib_df['Validations'].sum():,}"
        ]
    }
    summary_df = pd.DataFrame(summary_data)
    
    # Show summary
    st.dataframe(summary_df, use_container_width=True)
    
    # Download button
    @st.cache_data
    def convert_df_to_csv(df):
        return df.to_csv(index=False).encode('utf-8')
    
    csv = convert_df_to_csv(summary_df)
    st.download_button(
        label="📥 Download Summary Report (CSV)",
        data=csv,
        file_name="bhashadaan_summary_report.csv",
        mime="text/csv",
    )
    
    # Final insight
    st.markdown("---")
    st.markdown("""
    <div class="insight-box">
    <b>🎯 Key Takeaway:</b> Focus on converting new users to contributors through better onboarding 
    and engagement strategies. Prioritize language quality while growing contributions in 
    underrepresented languages. Use timing insights to maximize engagement.
    </div>
    """, unsafe_allow_html=True)