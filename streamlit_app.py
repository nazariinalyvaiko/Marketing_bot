import streamlit as st
import pandas as pd
import io
import sys
import asyncio
import os
from contextlib import redirect_stdout
from pathlib import Path
from datetime import datetime

from marketing_bot.segmentation.rfm import score_rfm
from marketing_bot.generation.openai_client import generate_marketing_text
from marketing_bot.generation.templates import EMAIL_TEMPLATE, SOCIAL_POST_TEMPLATE, render_prompt
from marketing_bot.senders.email_sender import EmailMessage, send_email
from marketing_bot.senders.social_sender import SocialPost, send_social_post
from marketing_bot.database.email_database import EmailDatabase
from marketing_bot.services.email_campaign_service import EmailCampaignService

# Page config
st.set_page_config(
    page_title="Marketing Bot Pro", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .campaign-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 Marketing Bot Pro</h1>
    <p>AI-powered email campaigns, social media posts, and customer segmentation with RFM analysis</p>
</div>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def get_services():
    return EmailDatabase(), EmailCampaignService()

db, campaign_service = get_services()

# API Configuration in Sidebar
with st.sidebar:
    st.header("⚙️ API Configuration")
    
    # OpenAI API Key
    openai_key = st.text_input(
        "OpenAI API Key", 
        type="password", 
        help="Your OpenAI API key for content generation",
        key="openai_api_key"
    )
    
    # SendGrid API Key  
    sendgrid_key = st.text_input(
        "SendGrid API Key", 
        type="password", 
        help="Your SendGrid API key for email sending",
        key="sendgrid_api_key"
    )
    
    # From Email
    from_email = st.text_input(
        "From Email", 
        value="marketing@yourcompany.com",
        help="Email address for sending campaigns",
        key="from_email"
    )
    
    st.markdown("---")
    
    # Mode settings
    st.subheader("🔧 Mode Settings")
    offline_mode = st.checkbox("Offline Mode (Mock content)", value=not bool(openai_key))
    dry_run = st.checkbox("Dry Run (Log only)", value=True)
    
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["OFFLINE_MODE"] = "false"
    else:
        os.environ["OFFLINE_MODE"] = "true"
        
    if sendgrid_key:
        os.environ["SENDGRID_API_KEY"] = sendgrid_key
        os.environ["SENDGRID_FROM_EMAIL"] = from_email
        
    os.environ["SENDER_DRY_RUN"] = str(dry_run).lower()
    
    # Status indicators
    st.markdown("---")
    st.subheader("�� Status")
    
    if openai_key:
        st.success("🟢 AI AI Generation Ready")
    else:
        st.warning("🟡 Using Mock Content")
        
    if sendgrid_key and not dry_run:
        st.success("🟢 Email Sending Active")
    else:
        st.info("🔵 Dry Run Mode")

# Main tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Segmentation", "✍️ AI Content Generation", "📧 Campaign Management", "📤 Send Messages"])

with tab1:
    st.header("RFM Customer Segmentation")
    st.markdown("Upload your customer data to automatically segment customers based on Recency, Frequency, and Monetary value.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Upload Customer CSV", 
            type=['csv'],
            help="CSV should contain: customer_id, recency_days, frequency, monetary_value"
        )
        
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.subheader("�� Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            if st.button("🚀 Run RFM Segmentation", type="primary"):
                with st.spinner("Running segmentation analysis..."):
                    scored = score_rfm(df)
                    st.session_state.segmented_data = scored
                
                st.success("✅ Segmentation completed!")
                
                # Show results
                segment_counts = scored['segment'].value_counts()
                
                col_chart, col_table = st.columns([1, 1])
                
                with col_chart:
                    st.subheader("📊 Segment Distribution")
                    st.bar_chart(segment_counts)
                
                with col_table:
                    st.subheader("📈 Segment Stats")
                    for segment, count in segment_counts.items():
                        st.metric(segment.replace('_', ' ').title(), count)
                
                # Download button
                csv = scored.to_csv(index=False)
                st.download_button(
                    label="📥 Download Segmented Data",
                    data=csv,
                    file_name="segmented_customers.csv",
                    mime="text/csv",
                    type="secondary"
                )
                
                # Option to save to database
                if st.button("💾 Save to Database"):
                    # Convert to contacts and save
                    contacts_data = []
                    for _, row in scored.iterrows():
                        contacts_data.append({
                            'email': f"customer_{row['customer_id']}@example.com",
                            'name': f"Customer {row['customer_id']}",
                            'segment': row['segment'],
                            'customer_id': row['customer_id'],
                            'recency_days': row['recency_days'],
                            'frequency': row['frequency'],
                            'monetary_value': row['monetary_value']
                        })
                    
                    contacts_df = pd.DataFrame(contacts_data)
                    temp_file = Path("temp_contacts.csv")
                    contacts_df.to_csv(temp_file, index=False)
                    
                    added_count = db.add_contacts_from_csv(temp_file, "auto_imported")
                    temp_file.unlink()
                    
                    st.success(f"✅ Added {added_count} contacts to database!")
    
    with col2:
        st.subheader("📋 Required CSV Format")
        st.code("""
customer_id,recency_days,frequency,monetary_value
C001,5,12,1200
C002,45,4,300
C003,12,8,650
        """)
        
        st.info("**Columns explained:**\n- **customer_id**: Unique customer identifier\n- **recency_days**: Days since last purchase\n- **frequency**: Number of purchases\n- **monetary_value**: Total spend amount")

with tab2:
    st.header("AI Content Generation")
    st.markdown("Generate personalized email campaigns and social media posts for different customer segments.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Campaign Settings")
        segment_name = st.selectbox(
            "Target Segment", 
            ["champions", "loyal_customers", "potential_loyalists", "new_customers", 
             "promising", "needs_attention", "about_to_sleep", "at_risk", "hibernating", "lost"],
            help="Choose the customer segment to target"
        )
        
        product_name = st.text_input("Product/Service", "Premium Widget Pro", key="gen_product")
        goal = st.text_input("Campaign Goal", "Drive summer sale conversions", key="gen_goal")
        offer = st.text_input("Special Offer", "25% off for 48 hours", key="gen_offer")
    
    with col2:
        st.subheader("✨ Content Options")
        tone = st.selectbox("Tone", ["friendly", "professional", "playful", "urgent"])
        platform = st.selectbox("Social Platform", ["twitter", "facebook", "instagram", "linkedin"])
        content_type = st.selectbox("Content Type", ["email", "social", "both"])
        max_tokens = st.slider("Max Tokens", 100, 500, 300)
    
    if st.button("🎨 Generate Content", type="primary"):
        ctx = {
            "segment_name": segment_name,
            "product_name": product_name,
            "goal": goal,
            "offer": offer,
            "tone": tone,
            "platform": platform,
        }
        
        if content_type in ("email", "both"):
            with st.spinner("Generating email content..."):
                email_prompt = render_prompt(EMAIL_TEMPLATE, ctx)
                email_content = generate_marketing_text(email_prompt, max_tokens=max_tokens)
            
            st.subheader("📧 Email Campaign")
            
            # Parse subject and body
            lines = [line.strip() for line in email_content.splitlines() if line.strip()]
            subject_line = next((l for l in lines if l.lower().startswith("subject:")), "")
            body_lines = [l for l in lines if not l.lower().startswith("subject:")]
            subject = subject_line.split(":", 1)[1].strip() if ":" in subject_line else "Your Exclusive Offer"
            body = "\n".join(body_lines)
            
            col_subj, col_body = st.columns([1, 2])
            
            with col_subj:
                st.text_input("Subject Line", value=subject, disabled=True, key="gen_subject_display")
            
            with col_body:
                st.text_area("Email Body", value=body, height=200, key="gen_email_body")
            
            # Save to session state for campaign creation
            st.session_state.generated_email = {
                'subject': subject,
                'body': body,
                'segment': segment_name
            }
        
        if content_type in ("social", "both"):
            with st.spinner("Generating social content..."):
                social_prompt = render_prompt(SOCIAL_POST_TEMPLATE, ctx)
                social_content = generate_marketing_text(social_prompt, max_tokens=max_tokens)
            
            st.subheader("📱 Social Media Post")
            st.text_area("Post Content", value=social_content, height=150, key="gen_social_content")
            
            # Save to session state
            st.session_state.generated_social = {
                'content': social_content,
                'platform': platform,
                'segment': segment_name
            }

with tab3:
    st.header("Campaign Management")
    st.markdown("Create and manage email campaigns for different customer segments.")
    
    # Show current contacts
    contact_stats = db.get_contact_count_by_segment()
    
    if contact_stats:
        st.subheader("📊 Current Database")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Contacts", sum(contact_stats.values()))
        with col2:
            st.metric("Segments", len(contact_stats))
        with col3:
            st.metric("Avg per Segment", round(sum(contact_stats.values()) / len(contact_stats)))
        
        # Show segment breakdown
        segment_df = pd.DataFrame(list(contact_stats.items()), columns=['Segment', 'Count'])
        st.bar_chart(segment_df.set_index('Segment'))
        
        # Create campaign from generated content
        if 'generated_email' in st.session_state:
            st.subheader("🎯 Create Campaign from Generated Content")
            
            with st.expander("📧 Email Campaign", expanded=True):
                email_data = st.session_state.generated_email
                
                campaign_name = st.text_input("Campaign Name", f"Campaign for {email_data['segment']}", key="camp_name")
                campaign_subject = st.text_input("Subject", email_data['subject'], key="camp_subject")
                campaign_body = st.text_area("Body", email_data['body'], height=200, key="camp_body")
                campaign_segment = st.selectbox("Target Segment", list(contact_stats.keys()), 
                                              index=list(contact_stats.keys()).index(email_data['segment']) 
                                              if email_data['segment'] in contact_stats.keys() else 0)
                
                if st.button("💾 Create Email Campaign", type="primary"):
                    campaign_id = asyncio.run(campaign_service.create_campaign(
                        name=campaign_name,
                        subject=campaign_subject,
                        body=campaign_body,
                        segment=campaign_segment
                    ))
                    st.success(f"✅ Email campaign created! ID: {campaign_id}")
        
        # Show existing campaigns
        campaigns_df = db.get_campaigns()
        if not campaigns_df.empty:
            st.subheader("📋 Existing Campaigns")
            st.dataframe(campaigns_df, use_container_width=True)
        
    else:
        st.warning("📝 No contacts in database. Please upload customer data first in the Segmentation tab.")

with tab4:
    st.header("Send Messages")
    st.markdown("Send individual messages or bulk campaigns to your contacts.")
    
    # Get contact stats
    contact_stats = db.get_contact_count_by_segment()
    
    if not contact_stats:
        st.warning("📝 No contacts in database. Please upload customer data first.")
    else:
        send_type = st.radio(
            "Choose sending method:",
            ["📧 Send to Individual", "📊 Send to Segment", "📱 Post to Social Media"],
            horizontal=True
        )
        
        if send_type == "📧 Send to Individual":
            st.subheader("Send Individual Email")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Get contacts for selection
                contacts = db.load_contacts()
                if contacts:
                    contact_options = {f"{c.email} ({c.name or 'No name'})": c.email for c in contacts}
                    selected_contact = st.selectbox("Select Recipient", list(contact_options.keys()))
                    recipient_email = contact_options[selected_contact]
                else:
                    recipient_email = st.text_input("Recipient Email", "customer@example.com")
                
                subject = st.text_input("Subject", "Your Exclusive Offer", key="individual_subject")
                body = st.text_area("Message Body", height=200, key="individual_body")
            
            with col2:
                # Show contact info
                if contacts:
                    selected_contact_obj = next((c for c in contacts if c.email == recipient_email), None)
                    if selected_contact_obj:
                        st.info(f"""
                        **Contact Info:**
                        - Name: {selected_contact_obj.name or 'N/A'}
                        - Segment: {selected_contact_obj.segment or 'N/A'}
                        - Customer ID: {selected_contact_obj.customer_id or 'N/A'}
                        """)
            
            if st.button("📨 Send Individual Email", type="primary"):
                msg = EmailMessage(subject=subject, body=body, to=recipient_email)
                
                with st.spinner("Sending email..."):
                    f = io.StringIO()
                    with redirect_stdout(f):
                        send_email(msg)
                    log_output = f.getvalue()
                
                st.success("✅ Email sent!")
                with st.expander("📋 View Log"):
                    st.code(log_output, language="text")
        
        elif send_type == "📊 Send to Segment":
            st.subheader("Send Campaign to Segment")
            
            # Select campaign
            campaigns_df = db.get_campaigns()
            if not campaigns_df.empty:
                selected_campaign = st.selectbox("Select Campaign", campaigns_df['name'].tolist())
                campaign_id = campaigns_df[campaigns_df['name'] == selected_campaign]['campaign_id'].iloc[0]
                
                # Select segment
                segment = st.selectbox("Target Segment", list(contact_stats.keys()))
                
                # Send options
                col1, col2 = st.columns(2)
                with col1:
                    max_emails = st.number_input("Max Emails to Send", min_value=1, max_value=contact_stats.get(segment, 0), value=min(10, contact_stats.get(segment, 0)))
                with col2:
                    dry_run = st.checkbox("Dry Run (Test mode)", value=True)
                
                if st.button("📤 Send Campaign to Segment", type="primary"):
                    with st.spinner(f"Sending campaign to {segment} segment..."):
                        result = asyncio.run(campaign_service.send_campaign(
                            campaign_id=campaign_id,
                            max_emails=max_emails,
                            dry_run=dry_run
                        ))
                    
                    st.success(f"✅ Campaign sent to {segment}!")
                    with st.expander("📋 View Results"):
                        st.json(result)
            else:
                st.warning("No campaigns available. Create a campaign first.")
        
        elif send_type == "📱 Post to Social Media":
            st.subheader("Post to Social Media")
            
            col1, col2 = st.columns(2)
            
            with col1:
                platforms = st.multiselect(
                    "Select Platforms",
                    ["twitter", "facebook", "instagram", "linkedin"],
                    default=["twitter"]
                )
                
                content = st.text_area("Post Content", height=200, key="social_content")
                
                # Add hashtags
                hashtags = st.text_input("Hashtags (comma separated)", "#marketing #ai #automation")
            
            with col2:
                st.info("""
                **Post Preview:**
                """)
                if content:
                    preview_content = content
                    if hashtags:
                        preview_content += f"\n\n{hashtags}"
                    st.text_area("Preview", preview_content, height=200, disabled=True)
            
            if st.button("📢 Post to Social Media", type="primary"):
                if platforms and content:
                    for platform in platforms:
                        post = SocialPost(platform=platform, content=content)
                        
                        with st.spinner(f"Posting to {platform}..."):
                            f = io.StringIO()
                            with redirect_stdout(f):
                                send_social_post(post)
                            log_output = f.getvalue()
                        
                        st.success(f"✅ Posted to {platform}!")
                        with st.expander(f"📋 {platform.title()} Log"):
                            st.code(log_output, language="text")
                else:
                    st.error("Please select platforms and enter content.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit • Marketing Bot Pro v2.0")

# Dark theme CSS
st.markdown("""
<style>
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background: #2d3748 !important;
            color: #e2e8f0 !important;
            border-left-color: #667eea !important;
        }
        .campaign-card {
            background: #4a5568 !important;
            color: #e2e8f0 !important;
            border-color: #718096 !important;
        }
        .success-message {
            background: #22543d !important;
            color: #9ae6b4 !important;
            border-color: #38a169 !important;
        }
        .warning-message {
            background: #744210 !important;
            color: #fbd38d !important;
            border-color: #ed8936 !important;
        }
    }
</style>
""", unsafe_allow_html=True)
