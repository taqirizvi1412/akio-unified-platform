import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
from collections import Counter
import re
import random

# Constants for file paths
TEMPLATES_FILE = "data/response_templates.json"
QUEUE_FILE = "data/email_queue.json"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Initialize session state variables
def initialize_session_state():
    """Initialize all required session state variables"""
    # Existing history
    if 'response_history' not in st.session_state:
        st.session_state.response_history = []
    
    # Email queue for priority system
    if 'email_queue' not in st.session_state:
        st.session_state.email_queue = load_queue()
    
    # Response templates
    if 'response_templates' not in st.session_state:
        st.session_state.response_templates = load_templates()
    
    # Search results
    if 'search_results' not in st.session_state:
        st.session_state.search_results = []
    
    # Analytics date range
    if 'analytics_date_range' not in st.session_state:
        st.session_state.analytics_date_range = 7  # Default to last 7 days

# =====================================================
# Feature 1: Email Priority Queue
# =====================================================

def calculate_priority_score(email_data):
    """
    Calculate priority score for an email
    Higher score = higher priority
    
    Factors:
    - Negative sentiment: +30 points
    - Urgency keywords: +20 points
    - Customer status (VIP): +15 points
    - Email age: +1 point per hour
    """
    score = 0
    
    # Sentiment factor
    if email_data.get('sentiment', 'Neutral') == 'Negative':
        score += 30
    elif email_data.get('sentiment', 'Neutral') == 'Neutral':
        score += 10
    
    # Urgency factor
    urgent_keywords = ['urgent', 'asap', 'immediately', 'emergency', 'critical']
    email_content = email_data.get('email', '').lower()
    if any(keyword in email_content for keyword in urgent_keywords):
        score += 20
    
    # Customer status (mock implementation - in real app, check customer database)
    vip_customers = ['Alex Martin', 'Sarah Johnson', 'Michael Chen']
    if email_data.get('customer_name', '') in vip_customers:
        score += 15
    
    # Email age factor
    try:
        email_time = datetime.strptime(email_data.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
        hours_old = (datetime.now() - email_time).total_seconds() / 3600
        score += min(int(hours_old), 24)  # Cap at 24 hours
    except:
        pass
    
    return score

def add_to_queue(email_data):
    """Add an email to the priority queue"""
    email_data['priority_score'] = calculate_priority_score(email_data)
    email_data['status'] = 'pending'
    email_data['queue_id'] = f"Q{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    st.session_state.email_queue.append(email_data)
    save_queue(st.session_state.email_queue)

def save_queue(queue_data):
    """Save queue to JSON file"""
    try:
        with open(QUEUE_FILE, 'w', encoding='utf-8') as f:
            json.dump(queue_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving queue: {str(e)}")

def load_queue():
    """Load queue from JSON file"""
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def render_priority_queue():
    """Render the email priority queue interface"""
    st.header("🎯 Email Priority Queue")
    
    # Filter pending emails and sort by priority
    pending_emails = [e for e in st.session_state.email_queue if e.get('status') == 'pending']
    pending_emails.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
    
    if not pending_emails:
        st.info("No pending emails in the queue. Great job! 🎉")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pending Emails", len(pending_emails))
    with col2:
        urgent_count = sum(1 for e in pending_emails if e.get('priority_score', 0) > 40)
        st.metric("Urgent Emails", urgent_count)
    with col3:
        avg_age = sum(e.get('priority_score', 0) for e in pending_emails) / len(pending_emails)
        st.metric("Avg Priority Score", f"{avg_age:.1f}")
    
    st.divider()
    
    # Display queue
    for idx, email in enumerate(pending_emails):
        # Determine priority color
        priority = email.get('priority_score', 0)
        if priority > 40:
            color = "🔴"  # High priority
            border_color = "#ff4b4b"
        elif priority > 20:
            color = "🟡"  # Medium priority
            border_color = "#ffa726"
        else:
            color = "🟢"  # Low priority
            border_color = "#00cc88"
        
        # Create email card
        with st.container():
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; padding-left: 10px;">
                <h4>{color} {email.get('customer_name', 'Unknown')} - {email.get('email_type', 'General')}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Email preview
                email_preview = email.get('email', '')[:150] + "..." if len(email.get('email', '')) > 150 else email.get('email', '')
                st.write(f"**Preview:** {email_preview}")
                
                # Metadata
                col_meta1, col_meta2, col_meta3 = st.columns(3)
                with col_meta1:
                    st.caption(f"Priority Score: {priority}")
                with col_meta2:
                    st.caption(f"Sentiment: {email.get('sentiment', 'Unknown')}")
                with col_meta3:
                    st.caption(f"Time: {email.get('timestamp', 'Unknown')}")
            
            with col2:
                if st.button("Process", key=f"process_{email.get('queue_id')}"):
                    # Mark as processed
                    for e in st.session_state.email_queue:
                        if e.get('queue_id') == email.get('queue_id'):
                            e['status'] = 'processed'
                            e['processed_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    save_queue(st.session_state.email_queue)
                    st.rerun()
        
        st.divider()

# =====================================================
# Feature 2: Smart Search & Filters
# =====================================================

def search_emails(query, filters=None):
    """
    Search through email history with filters
    Returns list of matching emails
    """
    results = []
    query_lower = query.lower() if query else ""
    
    for email in st.session_state.response_history:
        # Text search
        if query:
            searchable_fields = [
                email.get('email', ''),
                email.get('response', ''),
                email.get('customer_name', ''),
                ' '.join(email.get('keywords', []))
            ]
            
            if not any(query_lower in field.lower() for field in searchable_fields):
                continue
        
        # Apply filters
        if filters:
            # Date range filter
            if filters.get('start_date') and filters.get('end_date'):
                try:
                    email_date = datetime.strptime(email.get('timestamp', ''), "%Y-%m-%d %H:%M:%S").date()
                    if not (filters['start_date'] <= email_date <= filters['end_date']):
                        continue
                except:
                    continue
            
            # Sentiment filter
            if filters.get('sentiment') and filters['sentiment'] != 'All':
                if email.get('sentiment') != filters['sentiment']:
                    continue
            
            # Email type filter
            if filters.get('email_type') and filters['email_type'] != 'All':
                if email.get('email_type') != filters['email_type']:
                    continue
        
        results.append(email)
    
    return results

def highlight_search_term(text, search_term):
    """Highlight search terms in text"""
    if not search_term:
        return text
    
    # Use regex to find and highlight terms (case-insensitive)
    pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    highlighted = pattern.sub(lambda m: f"**{m.group()}**", text)
    return highlighted

def render_search_interface():
    """Render the search and filter interface"""
    st.header("🔍 Smart Search & Filters")
    
    # Search bar
    search_query = st.text_input(
        "Search emails, responses, customers, or keywords:",
        placeholder="Type to search...",
        help="Search across all email content, responses, customer names, and keywords"
    )
    
    # Quick filters
    st.subheader("Quick Filters")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_filter = None
    with col1:
        if st.button("Last 24 Hours", use_container_width=True):
            quick_filter = "last_24"
    with col2:
        if st.button("Negative Sentiment", use_container_width=True):
            quick_filter = "negative"
    with col3:
        if st.button("Urgent Only", use_container_width=True):
            quick_filter = "urgent"
    with col4:
        if st.button("This Week", use_container_width=True):
            quick_filter = "this_week"
    
    # Advanced filters
    with st.expander("Advanced Filters"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Date range
            st.subheader("Date Range")
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=7))
            end_date = st.date_input("End Date", value=datetime.now().date())
            
            # Sentiment filter
            sentiment_filter = st.selectbox(
                "Sentiment",
                ["All", "Positive", "Negative", "Neutral"]
            )
        
        with col2:
            # Email type filter
            email_types = ["All"] + list(set(e.get('email_type', 'Unknown') for e in st.session_state.response_history))
            email_type_filter = st.selectbox("Email Type", email_types)
            
            # Language filter
            languages = ["All"] + list(set(e.get('language', 'Unknown') for e in st.session_state.response_history))
            language_filter = st.selectbox("Language", languages)
    
    # Apply filters
    filters = {
        'start_date': start_date,
        'end_date': end_date,
        'sentiment': sentiment_filter if sentiment_filter != 'All' else None,
        'email_type': email_type_filter if email_type_filter != 'All' else None
    }
    
    # Handle quick filters
    if quick_filter == "last_24":
        filters['start_date'] = (datetime.now() - timedelta(days=1)).date()
        filters['end_date'] = datetime.now().date()
    elif quick_filter == "negative":
        filters['sentiment'] = 'Negative'
    elif quick_filter == "urgent":
        search_query = "urgent"
    elif quick_filter == "this_week":
        filters['start_date'] = (datetime.now() - timedelta(days=7)).date()
        filters['end_date'] = datetime.now().date()
    
    # Perform search
    if search_query or any(filters.values()):
        results = search_emails(search_query, filters)
        
        # Display results
        st.divider()
        st.subheader(f"Search Results ({len(results)} found)")
        
        if results:
            for idx, result in enumerate(results[:20]):  # Limit to 20 results
                with st.expander(
                    f"{result.get('customer_name', 'Unknown')} - {result.get('email_type', 'Unknown')} - {result.get('timestamp', 'Unknown')}"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Original Email:**")
                        email_text = highlight_search_term(result.get('email', ''), search_query)
                        st.markdown(email_text[:500] + "..." if len(email_text) > 500 else email_text)
                        
                        st.write(f"**Sentiment:** {result.get('sentiment', 'Unknown')}")
                        st.write(f"**Keywords:** {', '.join(result.get('keywords', []))}")
                    
                    with col2:
                        st.write("**Generated Response:**")
                        response_text = highlight_search_term(result.get('response', ''), search_query)
                        st.markdown(response_text[:500] + "..." if len(response_text) > 500 else response_text)
        else:
            st.info("No results found. Try adjusting your search criteria.")

# =====================================================
# Feature 3: Enhanced Analytics Dashboard
# =====================================================

def calculate_analytics_metrics(history_data, date_range_days=7):
    """Calculate analytics metrics from history"""
    # Filter data by date range
    cutoff_date = datetime.now() - timedelta(days=date_range_days)
    filtered_data = []
    
    for item in history_data:
        try:
            item_date = datetime.strptime(item.get('timestamp', ''), "%Y-%m-%d %H:%M:%S")
            if item_date >= cutoff_date:
                filtered_data.append(item)
        except:
            continue
    
    # Calculate metrics
    metrics = {
        'total_emails': len(filtered_data),
        'emails_today': 0,
        'avg_response_time': 0,  # Mock value - would calculate from actual response times
        'sentiment_distribution': Counter(),
        'email_types': Counter(),
        'languages': Counter(),
        'keywords': Counter(),
        'daily_volume': {}
    }
    
    # Count emails today
    today = datetime.now().date()
    for item in filtered_data:
        try:
            item_date = datetime.strptime(item.get('timestamp', ''), "%Y-%m-%d %H:%M:%S").date()
            if item_date == today:
                metrics['emails_today'] += 1
            
            # Count by date for daily volume
            date_str = item_date.strftime("%Y-%m-%d")
            metrics['daily_volume'][date_str] = metrics['daily_volume'].get(date_str, 0) + 1
        except:
            continue
    
    # Sentiment distribution
    for item in filtered_data:
        sentiment = item.get('sentiment', 'Unknown')
        metrics['sentiment_distribution'][sentiment] += 1
    
    # Email types
    for item in filtered_data:
        email_type = item.get('email_type', 'Unknown')
        metrics['email_types'][email_type] += 1
    
    # Languages
    for item in filtered_data:
        language = item.get('language', 'Unknown')
        metrics['languages'][language] += 1
    
    # Keywords (top 10)
    all_keywords = []
    for item in filtered_data:
        all_keywords.extend(item.get('keywords', []))
    metrics['keywords'] = Counter(all_keywords).most_common(10)
    
    # Mock response time (in production, calculate actual times)
    metrics['avg_response_time'] = random.uniform(2.5, 5.5)
    
    return metrics

def render_analytics_dashboard():
    """Render the analytics dashboard"""
    st.header("📊 Analytics Dashboard")
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        date_range = st.selectbox(
            "Select Time Period",
            options=[7, 14, 30, 90],
            format_func=lambda x: f"Last {x} days",
            index=0
        )
        st.session_state.analytics_date_range = date_range
    
    with col3:
        if st.button("Export Analytics"):
            # Create analytics report
            metrics = calculate_analytics_metrics(st.session_state.response_history, date_range)
            report = {
                'generated_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'date_range_days': date_range,
                'metrics': {k: v for k, v in metrics.items() if k != 'daily_volume'}
            }
            
            # Convert to JSON and offer download
            json_str = json.dumps(report, indent=2, default=str)
            st.download_button(
                label="Download Report (JSON)",
                data=json_str,
                file_name=f"analytics_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    # Calculate metrics
    metrics = calculate_analytics_metrics(st.session_state.response_history, date_range)
    
    # Display key metrics
    st.subheader("Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Emails",
            metrics['total_emails'],
            delta=f"{metrics['emails_today']} today"
        )
    
    with col2:
        st.metric(
            "Avg Response Time",
            f"{metrics['avg_response_time']:.1f} min",
            delta="-12%" if metrics['avg_response_time'] < 4 else "+8%"
        )
    
    with col3:
        negative_pct = (metrics['sentiment_distribution'].get('Negative', 0) / max(metrics['total_emails'], 1)) * 100
        st.metric(
            "Negative Sentiment",
            f"{negative_pct:.1f}%",
            delta="-2.3%" if negative_pct < 20 else "+1.2%"
        )
    
    with col4:
        most_common_type = metrics['email_types'].most_common(1)[0][0] if metrics['email_types'] else 'None'
        st.metric(
            "Top Issue Type",
            most_common_type,
            delta=None
        )
    
    st.divider()
    
    # Charts - using simple text-based visualization
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily volume display
        st.subheader("Daily Email Volume")
        if metrics['daily_volume']:
            st.write("**Email count by date:**")
            dates = sorted(metrics['daily_volume'].keys())
            for date in dates[-7:]:  # Show last 7 days
                count = metrics['daily_volume'][date]
                bar = "█" * min(count, 20)  # Visual bar with max 20 blocks
                st.text(f"{date}: {bar} ({count})")
        else:
            st.info("No data available for the selected period")
        
        # Sentiment distribution
        st.subheader("Sentiment Distribution")
        if metrics['sentiment_distribution']:
            total = sum(metrics['sentiment_distribution'].values())
            for sentiment, count in metrics['sentiment_distribution'].items():
                percentage = (count / total) * 100
                bar = "█" * int(percentage / 5)  # Scale to fit
                st.text(f"{sentiment}: {bar} {percentage:.1f}% ({count})")
    
    with col2:
        # Top keywords
        st.subheader("Top 10 Keywords")
        if metrics['keywords']:
            st.write("**Most frequent keywords:**")
            for i, (keyword, count) in enumerate(metrics['keywords'], 1):
                st.text(f"{i}. {keyword}: {count}")
        else:
            st.info("No keywords found")
        
        # Language distribution
        st.subheader("Language Distribution")
        if metrics['languages']:
            total = metrics['total_emails']
            for lang, count in metrics['languages'].items():
                percentage = (count / total) * 100
                st.write(f"• **{lang}**: {percentage:.1f}% ({count} emails)")
        else:
            st.info("No language data available")

# =====================================================
# Feature 4: Smart Response Templates Manager
# =====================================================

def load_templates():
    """Load templates from JSON file"""
    if os.path.exists(TEMPLATES_FILE):
        try:
            with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return get_default_templates()
    return get_default_templates()

def save_templates(templates):
    """Save templates to JSON file"""
    try:
        os.makedirs(os.path.dirname(TEMPLATES_FILE), exist_ok=True)
        with open(TEMPLATES_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error saving templates: {str(e)}")
        return False

def get_default_templates():
    """Get default templates if none exist"""
    return [
        {
            'id': 'tpl_001',
            'name': 'Friendly Greeting',
            'category': 'General',
            'language': 'English',
            'sentiment': 'Neutral',
            'content': 'Dear {{customer_name}},\n\nThank you for contacting us. {{greeting_message}}\n\n',
            'variables': ['customer_name', 'greeting_message']
        },
        {
            'id': 'tpl_002',
            'name': 'Apology Opening',
            'category': 'Complaint',
            'language': 'English',
            'sentiment': 'Negative',
            'content': 'Dear {{customer_name}},\n\nI sincerely apologize for {{issue_description}}. We take your concerns very seriously.\n\n',
            'variables': ['customer_name', 'issue_description']
        },
        {
            'id': 'tpl_003',
            'name': 'Ticket Reference',
            'category': 'Technical',
            'language': 'English',
            'sentiment': 'Neutral',
            'content': 'Your ticket number is {{ticket_number}}. Our team will respond within {{response_time}}.\n\n',
            'variables': ['ticket_number', 'response_time']
        }
    ]

def replace_template_variables(template_content, variables_dict):
    """Replace template variables with actual values"""
    result = template_content
    for var, value in variables_dict.items():
        result = result.replace(f"{{{{{var}}}}}", value)
    return result

def render_template_manager():
    """Render the template management interface"""
    st.header("📝 Smart Response Templates")
    
    # Template operations
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("Template Library")
    
    with col2:
        if st.button("➕ New Template", use_container_width=True):
            st.session_state.creating_template = True
    
    with col3:
        # Export/Import templates
        export_import = st.selectbox(
            "Actions", 
            ["Actions", "Export Templates", "Import Templates"],
            label_visibility="collapsed"
        )
        
        if export_import == "Export Templates":
            templates_json = json.dumps(st.session_state.response_templates, indent=2)
            st.download_button(
                label="Download Templates",
                data=templates_json,
                file_name="response_templates.json",
                mime="application/json"
            )
        elif export_import == "Import Templates":
            uploaded_file = st.file_uploader("Choose a JSON file", type="json")
            if uploaded_file:
                try:
                    imported_templates = json.load(uploaded_file)
                    st.session_state.response_templates = imported_templates
                    save_templates(imported_templates)
                    st.success("Templates imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing templates: {str(e)}")
    
    st.divider()
    
    # Create/Edit template form
    if hasattr(st.session_state, 'creating_template') and st.session_state.creating_template:
        st.subheader("Create New Template")
        
        with st.form("new_template_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                template_name = st.text_input("Template Name", placeholder="e.g., Refund Confirmation")
                template_category = st.selectbox("Category", ["General", "Complaint", "Technical", "Billing", "Inquiry"])
                template_language = st.selectbox("Language", ["English", "French", "Spanish", "German"])
            
            with col2:
                template_sentiment = st.selectbox("Sentiment", ["Positive", "Neutral", "Negative"])
                template_variables = st.text_input(
                    "Variables (comma-separated)",
                    placeholder="customer_name, order_number, date",
                    help="Use {{variable_name}} in your template content"
                )
            
            template_content = st.text_area(
                "Template Content",
                height=200,
                placeholder="Dear {{customer_name}},\n\nThank you for your email regarding {{subject}}...",
                help="Use {{variable_name}} format for variables"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Save Template", type="primary", use_container_width=True):
                    if template_name and template_content:
                        new_template = {
                            'id': f"tpl_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                            'name': template_name,
                            'category': template_category,
                            'language': template_language,
                            'sentiment': template_sentiment,
                            'content': template_content,
                            'variables': [v.strip() for v in template_variables.split(',') if v.strip()]
                        }
                        st.session_state.response_templates.append(new_template)
                        save_templates(st.session_state.response_templates)
                        st.session_state.creating_template = False
                        st.success("Template created successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in all required fields")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.creating_template = False
                    st.rerun()
    
    # Display templates
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_category = st.selectbox("Filter by Category", ["All"] + ["General", "Complaint", "Technical", "Billing", "Inquiry"])
    with col2:
        filter_language = st.selectbox("Filter by Language", ["All"] + ["English", "French", "Spanish", "German"])
    with col3:
        filter_sentiment = st.selectbox("Filter by Sentiment", ["All"] + ["Positive", "Neutral", "Negative"])
    
    # Filter templates
    filtered_templates = st.session_state.response_templates
    if filter_category != "All":
        filtered_templates = [t for t in filtered_templates if t.get('category') == filter_category]
    if filter_language != "All":
        filtered_templates = [t for t in filtered_templates if t.get('language') == filter_language]
    if filter_sentiment != "All":
        filtered_templates = [t for t in filtered_templates if t.get('sentiment') == filter_sentiment]
    
    # Display filtered templates
    for template in filtered_templates:
        # Check if template has required fields
        if 'name' not in template or 'category' not in template or 'language' not in template:
            continue
            
        with st.expander(f"{template['name']} ({template['category']} - {template['language']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Category:** {template.get('category', 'Unknown')}")
                st.write(f"**Language:** {template.get('language', 'Unknown')}")
                st.write(f"**Sentiment:** {template.get('sentiment', 'Unknown')}")
                
                if template.get('variables'):
                    st.write(f"**Variables:** {', '.join(template['variables'])}")
                
                st.text_area("Content", value=template.get('content', ''), height=150, disabled=True, key=f"content_{template.get('id', '')}")
                
                # Variable preview
                if template.get('variables'):
                    st.subheader("Preview with Variables")
                    variable_values = {}
                    for var in template['variables']:
                        value = st.text_input(f"{var}:", key=f"var_{template.get('id', '')}_{var}", placeholder=f"Enter {var}")
                        if value:
                            variable_values[var] = value
                    
                    if variable_values:
                        preview = replace_template_variables(template.get('content', ''), variable_values)
                        st.text_area("Preview", value=preview, height=150, disabled=True, key=f"preview_{template.get('id', '')}")
            
            with col2:
                st.write("")  # Spacer
                if st.button("📋 Copy", key=f"copy_{template.get('id', '')}", use_container_width=True):
                    st.write("Copied to clipboard!")
                
                if st.button("🗑️ Delete", key=f"delete_{template.get('id', '')}", use_container_width=True):
                    st.session_state.response_templates = [t for t in st.session_state.response_templates if t.get('id') != template.get('id')]
                    save_templates(st.session_state.response_templates)
                    st.rerun()

# =====================================================
# Feature 5: Email Response Generation (Main Feature)
# =====================================================

def load_test_emails(filename="emails.txt"):
    """Load test emails from a text file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split emails by the separator
        emails = []
        email_sections = content.split('--- Email')
        
        for section in email_sections[1:]:  # Skip the first empty split
            lines = section.strip().split('\n')
            if lines:
                # Extract title from the first line
                title_line = lines[0].strip()
                title = title_line.rstrip(' ---').split(':', 1)[1].strip() if ':' in title_line else f"Email {len(emails) + 1}"
                
                # Get the email content (skip the title line)
                email_content = '\n'.join(lines[1:]).strip()
                
                if email_content:
                    emails.append({
                        'title': title,
                        'content': email_content
                    })
        
        return emails
    except FileNotFoundError:
        return None
    except Exception as e:
        st.error(f"Error loading test emails: {str(e)}")
        return None

def analyze_email(email_content):
    """Analyze email for sentiment, language, type, etc."""
    # Sentiment analysis
    sentiment = "Neutral"
    positive_words = ['thank', 'excellent', 'great', 'happy', 'pleased', 'wonderful']
    negative_words = ['problem', 'issue', 'disappointed', 'frustrated', 'angry', 'upset']
    
    email_lower = email_content.lower()
    positive_count = sum(1 for word in positive_words if word in email_lower)
    negative_count = sum(1 for word in negative_words if word in email_lower)
    
    if positive_count > negative_count:
        sentiment = "Positive"
    elif negative_count > positive_count:
        sentiment = "Negative"
    
    # Language detection
    language = "English"
    if any(word in email_lower for word in ['bonjour', 'merci', 'vous']):
        language = "French"
    elif any(word in email_lower for word in ['hola', 'gracias', 'usted']):
        language = "Spanish"
    elif any(word in email_lower for word in ['hallo', 'danke', 'sie']):
        language = "German"
    
    # Email type detection
    email_type = "General Inquiry"
    if any(word in email_lower for word in ['refund', 'money back', 'reimburse']):
        email_type = "Refund Request"
    elif any(word in email_lower for word in ['complaint', 'disappointed', 'frustrated']):
        email_type = "Complaint"
    elif any(word in email_lower for word in ['technical', 'error', 'bug', 'not working']):
        email_type = "Technical Support"
    elif any(word in email_lower for word in ['order', 'tracking', 'delivery']):
        email_type = "Order Status"
    
    # Extract keywords
    keywords = []
    important_words = ['urgent', 'refund', 'order', 'problem', 'help', 'issue', 'error', 
                      'delivery', 'account', 'payment', 'subscription', 'cancel']
    for word in important_words:
        if word in email_lower:
            keywords.append(word)
    
    return {
        'sentiment': sentiment,
        'language': language,
        'email_type': email_type,
        'keywords': keywords[:5]
    }

def generate_mock_response(email_content, analysis):
    """Generate a mock response based on email analysis"""
    customer_name = "Valued Customer"
    
    # Try to extract customer name
    lines = email_content.strip().split('\n')
    for i in range(len(lines)-1, -1, -1):
        line = lines[i].strip()
        if line and not any(word in line.lower() for word in ['thank', 'regards', 'best', 'sincerely']):
            words = line.split()
            if 1 <= len(words) <= 4 and all(word.replace('-', '').replace("'", '').isalpha() for word in words):
                if any(word[0].isupper() for word in words):
                    customer_name = line
                    break
    
    # Generate response based on email type
    if analysis['email_type'] == "Refund Request":
        response = f"""Dear {customer_name},

Thank you for contacting us about your refund request. I understand your concern and I'm here to help.

I've reviewed your account and initiated the refund process. Here's what you can expect:

• The refund will be processed within 3-5 business days
• You'll receive a confirmation email once it's complete
• The amount will be credited to your original payment method

Your reference number is: REF-{datetime.now().strftime('%Y%m%d')}-001

If you have any questions or don't see the refund within the timeframe, please don't hesitate to contact us.

Best regards,
Customer Service Team"""
    
    elif analysis['email_type'] == "Complaint":
        response = f"""Dear {customer_name},

I sincerely apologize for the experience you've had. Your satisfaction is extremely important to us, and I understand your frustration.

I've escalated your concern to our management team, and here's what we're doing:

• Investigating the issue immediately
• Implementing measures to prevent this from happening again
• Applying a goodwill gesture to your account

We value your feedback and are committed to making this right. A senior member of our team will contact you within 24 hours.

Thank you for bringing this to our attention.

Best regards,
Customer Service Team"""
    
    elif analysis['email_type'] == "Technical Support":
        response = f"""Dear {customer_name},

Thank you for reporting this technical issue. I'm here to help you resolve it as quickly as possible.

Based on your description, here are some immediate steps to try:

1. Clear your browser cache and cookies
2. Log out and log back into your account
3. Try using a different browser or device

If these steps don't resolve the issue, please provide:
• Your device type and operating system
• The browser you're using
• Any error messages you see

I'll monitor your case personally to ensure it's resolved promptly.

Best regards,
Customer Service Team"""
    
    else:  # General inquiry
        response = f"""Dear {customer_name},

Thank you for contacting us. I've carefully reviewed your message and I'm here to assist you.

Based on your inquiry, I'll be happy to help you with the information you need. Our team is committed to providing you with the best possible service.

Please let me know if you need any clarification or have additional questions. We're here to help!

Best regards,
Customer Service Team"""
    
    return response

def render_email_response_generator():
    """Render the main email response generation interface"""
    st.header("📧 Email Response Generator")
    
    # Load test emails if available
    test_emails = load_test_emails()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Email Input")
        
        # Test email selector if available
        if test_emails:
            st.markdown("#### 🧪 Test Email Selector")
            
            email_options = ["-- Select a test email --"] + [f"{i+1}. {email['title']}" for i, email in enumerate(test_emails)]
            selected_email = st.selectbox(
                "Choose a pre-written test email:",
                options=email_options,
                help="Select a test email to auto-populate the input field"
            )
            
            if selected_email != "-- Select a test email --":
                email_index = email_options.index(selected_email) - 1
                default_email = test_emails[email_index]['content']
            else:
                default_email = ""
            
            st.markdown("---")
        else:
            default_email = ""
            if os.path.exists("emails.txt"):
                st.info("Test emails file found but couldn't be parsed. Check the file format.")
            else:
                st.info("💡 Tip: Create an 'emails.txt' file with test emails for quick testing.")
        
        # Email input area
        email_input = st.text_area(
            "Paste or edit the customer email:",
            height=350,
            value=default_email,
            placeholder="Dear Support Team,\n\nI need help with...",
            key="email_input_main"
        )
        
        # Generate button
        if st.button("🚀 Generate Response", type="primary", use_container_width=True):
            if email_input:
                # Analyze email
                analysis = analyze_email(email_input)
                
                # Generate response
                response = generate_mock_response(email_input, analysis)
                
                # Create history entry
                history_entry = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'email': email_input,
                    'response': response,
                    'sentiment': analysis['sentiment'],
                    'language': analysis['language'],
                    'email_type': analysis['email_type'],
                    'keywords': analysis['keywords'],
                    'customer_name': "Valued Customer",  # Would be extracted in real implementation
                    'word_count': len(email_input.split()),
                    'urgent': 'urgent' in email_input.lower()
                }
                
                # Add to history
                st.session_state.response_history.append(history_entry)
                
                # Optionally add to queue
                if st.checkbox("Add to priority queue", value=True):
                    add_to_queue(history_entry)
                
                st.success("Response generated successfully!")
            else:
                st.error("Please enter an email to process")
    
    with col2:
        st.subheader("Generated Response & Analysis")
        
        if st.session_state.response_history:
            latest = st.session_state.response_history[-1]
            
            # Analysis summary
            st.markdown("### 📊 Email Analysis")
            
            col_a1, col_a2, col_a3 = st.columns(3)
            with col_a1:
                st.metric("Sentiment", latest['sentiment'])
            with col_a2:
                st.metric("Language", latest['language'])
            with col_a3:
                st.metric("Type", latest['email_type'])
            
            if latest['keywords']:
                st.write(f"**Keywords:** {', '.join(latest['keywords'])}")
            
            st.divider()
            
            # Generated response
            st.markdown("### 💬 Generated Response")
            response_text = st.text_area(
                "Response (editable):",
                value=latest['response'],
                height=300,
                key="response_edit"
            )
            
            # Action buttons
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("📋 Copy Response", use_container_width=True):
                    st.info("Response copied to clipboard!")
            with col_b2:
                if st.button("💾 Save as Template", use_container_width=True):
                    st.info("Template saved!")
        else:
            st.info("Generated response will appear here after processing an email")

# =====================================================
# Updated Integration Functions
# =====================================================

def render_enhanced_features():
    """
    Main function to render all enhanced features in tabs
    This should be integrated into your existing main app
    """
    # Initialize session state
    initialize_session_state()
    
    # Create tabs for features - NOW INCLUDING EMAIL RESPONSE
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📧 Email Response",
        "🔍 Search & Filters",
        "📝 Templates",
        "📊 Analytics",
        "🎯 Priority Queue"
    ])
    
    with tab1:
        render_email_response_generator()
    
    with tab2:
        render_search_interface()
    
    with tab3:
        render_template_manager()
    
    with tab4:
        render_analytics_dashboard()
    
    with tab5:
        render_priority_queue()

# Example integration with existing app
def integrate_with_existing_app():
    """
    Example of how to integrate these features into your existing email assistant
    Add this to your main app after the existing functionality
    """
    st.divider()
    st.header("🚀 Enhanced Features")
    render_enhanced_features()

# Standalone testing
if __name__ == "__main__":
    st.set_page_config(page_title="Email Assistant Enhanced Features", layout="wide")
    st.title("Email Assistant - Enhanced Features Demo")
    
    # Mock data for testing
    if 'response_history' not in st.session_state:
        st.session_state.response_history = [
            {
                'timestamp': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
                'email': 'I need urgent help with my account access. I cannot login!',
                'response': 'I understand you\'re having trouble accessing your account...',
                'customer_name': 'John Doe',
                'sentiment': 'Negative',
                'email_type': 'Technical Support',
                'language': 'English',
                'keywords': ['urgent', 'help', 'account', 'login']
            },
            {
                'timestamp': (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
                'email': 'Thank you for the excellent service!',
                'response': 'We\'re delighted to hear you had a positive experience...',
                'customer_name': 'Jane Smith',
                'sentiment': 'Positive',
                'email_type': 'Feedback',
                'language': 'English',
                'keywords': ['thank', 'excellent', 'service']
            }
        ]
    
    render_enhanced_features()