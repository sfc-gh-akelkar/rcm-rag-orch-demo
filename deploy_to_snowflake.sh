#!/bin/bash
# ========================================================================
# RCM Intelligence Hub - Deployment Script for Streamlit in Snowflake
# ========================================================================
# This script automates the deployment of the RCM Intelligence Hub
# to Streamlit in Snowflake with Native Cortex Agent
# ========================================================================

set -e  # Exit on error

echo "======================================================================"
echo "RCM Intelligence Hub - Streamlit in Snowflake Deployment"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check prerequisites
echo "Step 1: Checking prerequisites..."
echo ""

# Check if Snowflake CLI is installed
if ! command -v snow &> /dev/null; then
    echo -e "${RED}❌ Snowflake CLI not found${NC}"
    echo "Install with: pip install snowflake-cli-labs"
    exit 1
else
    echo -e "${GREEN}✅ Snowflake CLI installed${NC}"
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python 3 installed${NC}"
fi

# Check if required files exist
if [ ! -f "streamlit_app.py" ]; then
    echo -e "${RED}❌ streamlit_app.py not found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ streamlit_app.py found${NC}"
fi

if [ ! -f "snowflake.yml" ]; then
    echo -e "${RED}❌ snowflake.yml not found${NC}"
    exit 1
else
    echo -e "${GREEN}✅ snowflake.yml found${NC}"
fi

echo ""

# Step 2: Check Snowflake connection
echo "Step 2: Verifying Snowflake connection..."
echo ""

# Prompt for connection name
read -p "Enter Snowflake connection name (default: rcm_demo): " CONNECTION_NAME
CONNECTION_NAME=${CONNECTION_NAME:-rcm_demo}

# Test connection
if snow connection test --connection "$CONNECTION_NAME" &> /dev/null; then
    echo -e "${GREEN}✅ Connection '$CONNECTION_NAME' verified${NC}"
else
    echo -e "${YELLOW}⚠️  Connection '$CONNECTION_NAME' not configured${NC}"
    echo ""
    echo "Would you like to configure it now? (y/n)"
    read -p "> " CONFIGURE
    
    if [ "$CONFIGURE" = "y" ]; then
        echo ""
        echo "Configuring Snowflake connection..."
        snow connection add
    else
        echo -e "${RED}❌ Cannot proceed without valid connection${NC}"
        exit 1
    fi
fi

echo ""

# Step 3: Verify SQL setup
echo "Step 3: Verifying Snowflake setup..."
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT: Ensure you have executed these SQL scripts:${NC}"
echo "   1. 01_rcm_data_setup.sql"
echo "   2. 02_rcm_documents_setup.sql"
echo "   3. 03_rcm_data_generation.sql"
echo "   4. 04_rcm_semantic_views.sql"
echo "   5. 05_rcm_cortex_search.sql"
echo "   6. 06_rcm_agent_setup.sql"
echo "   7. 07_rcm_native_agent_production.sql ← NEW (Production Agent)"
echo ""
read -p "Have you executed all 7 SQL setup scripts? (y/n): " SCRIPTS_DONE

if [ "$SCRIPTS_DONE" != "y" ]; then
    echo -e "${RED}❌ Please execute all setup scripts first${NC}"
    echo "See: DEPLOYMENT_GUIDE_SIS.md for instructions"
    exit 1
fi

echo -e "${GREEN}✅ SQL setup confirmed${NC}"
echo ""

# Step 4: Deploy to Snowflake
echo "Step 4: Deploying Streamlit app to Snowflake..."
echo ""

# Confirm deployment
read -p "Deploy 'rcm_intelligence_hub' to Snowflake? (y/n): " CONFIRM_DEPLOY

if [ "$CONFIRM_DEPLOY" != "y" ]; then
    echo "Deployment cancelled"
    exit 0
fi

echo ""
echo "Deploying..."

# Deploy with Snowflake CLI
if snow streamlit deploy \
    --connection "$CONNECTION_NAME" \
    --replace \
    --open; then
    
    echo ""
    echo "======================================================================"
    echo -e "${GREEN}✅ DEPLOYMENT SUCCESSFUL!${NC}"
    echo "======================================================================"
    echo ""
    echo "Your RCM Intelligence Hub is now running in Snowflake!"
    echo ""
    echo "Access it via:"
    echo "  1. Snowsight → Projects → Streamlit → rcm_intelligence_hub"
    echo "  2. Or use the URL that just opened in your browser"
    echo ""
    echo "Next steps:"
    echo "  - Test with sample queries"
    echo "  - Configure RBAC for users"
    echo "  - Monitor usage in query history"
    echo ""
    echo "Documentation: DEPLOYMENT_GUIDE_SIS.md"
    echo "======================================================================"
    
else
    echo ""
    echo "======================================================================"
    echo -e "${RED}❌ DEPLOYMENT FAILED${NC}"
    echo "======================================================================"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check connection: snow connection test --connection $CONNECTION_NAME"
    echo "  2. Verify permissions on RCM_AI_DEMO database"
    echo "  3. Ensure warehouse RCM_INTELLIGENCE_WH is running"
    echo "  4. See DEPLOYMENT_GUIDE_SIS.md for detailed troubleshooting"
    echo ""
    exit 1
fi

