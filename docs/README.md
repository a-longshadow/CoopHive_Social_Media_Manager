# CoopHive Social Media Manager Documentation

## Overview

This directory contains comprehensive documentation for the CoopHive Social Media Manager Django application. The documentation covers all aspects of the system from basic setup to advanced n8n integration.

## Documentation Structure

### 📚 Core Documentation

#### [API Documentation](api.md)
Complete REST API reference covering all platform endpoints and n8n integration APIs.
- **n8n Workflow Integration APIs**: Duplicate checking and tweet storage endpoints
- **Twitter/X.com APIs**: Scraped tweets management and generated content APIs  
- **LinkedIn APIs**: Professional posting and article sharing
- **Farcaster APIs**: Decentralized social protocol integration
- **Bluesky APIs**: AT Protocol-based social networking

#### [Database Models](models.md) 
Comprehensive database schema documentation with model relationships.
- **Authentication Models**: User management, verification codes, auth events
- **Core Models**: Campaigns, posts, media assets with inheritance patterns
- **Twitter n8n Models**: SourceTweet, CampaignBatch, GeneratedTweet for AI workflow
- **Platform Models**: TwitterPost, LinkedInPost, FarcasterPost, BlueskyPost
- **Settings Models**: Database-first configuration management

#### [Configuration Guide](configuration.md)
Django settings, environment variables, and deployment configuration.
- **Database-First Email System**: Runtime email configuration with environment fallback
- **Google OAuth Setup**: Working TaskForge-style OAuth with domain restrictions
- **Super Admin System**: Hardcoded admin users with automatic creation
- **Platform API Configuration**: Social media platform integration settings

#### [Development Guide](development.md)
Complete development setup, project structure, and coding guidelines.
- **Project Architecture**: Modular Django app structure with platform separation
- **Authentication System**: Custom backends, Google OAuth, domain restrictions
- **Database-First Settings**: Runtime configuration without deployment
- **Modern UI System**: TaskForge-styled templates with responsive design

### 🔧 Integration Documentation  

#### [Twitter/X-Bot Integration Guide](twitter_x_bot_integration_guide.md)
**NEW**: Comprehensive guide for n8n workflow integration with Django.
- **Complete Data Flow**: From social listening to AI generation to human approval
- **Phase-by-Phase Implementation**: Source ingestion, AI processing, content review
- **API Endpoint Specifications**: Exact request/response formats for n8n
- **Database Models**: Detailed schema for Twitter n8n integration
- **Testing and Debugging**: Comprehensive troubleshooting and monitoring

#### [Platform Apps Guide](platform_apps_guide.md)
**NEW**: Detailed documentation for all social media platform integrations.
- **Twitter/X.com**: Advanced n8n integration with AI-powered content generation
- **LinkedIn**: Professional networking with article and document support
- **Farcaster**: Decentralized social protocol with channel management
- **Bluesky**: AT Protocol integration with content labeling
- **Cross-Platform Features**: Unified campaign management and shared infrastructure

#### [n8n Duplicate Check API](n8n_duplicate_check_api.md)
Technical specification for the primary n8n integration endpoint.
- **Endpoint Details**: `/twitter/api/check-duplicate-tweet/` specification
- **Input/Output Formats**: Exact JSON schemas for n8n workflow
- **Database Integration**: SourceTweet model and duplicate detection logic
- **Testing Examples**: curl and Python test examples

#### [n8n Receive Tweets API](n8n_receive_tweets_api.md)  
Technical specification for AI-generated content storage endpoint.
- **Endpoint Details**: `/twitter/api/receive-tweets/` specification
- **Campaign Batch Management**: CampaignBatch and GeneratedTweet models
- **AI Metadata Storage**: Brand alignment scores and voice patterns
- **Review Workflow Integration**: Connection to human approval process

### 🧪 Testing & Quality

#### [Testing Guide](testing.md)
**UPDATED**: Comprehensive testing documentation with current test structure.
- **Authentication Tests**: 24 comprehensive tests for login, OAuth, password reset
- **Platform Integration Tests**: API endpoints, model validation, view functionality  
- **n8n Integration Tests**: Duplicate detection, campaign storage, error handling
- **Testing Patterns**: Best practices, mocking, performance testing

#### [Forms Documentation](forms.md)
Form validation, custom template tags, and modern UI patterns.
- **TaskForge-Style Forms**: Modern authentication forms with Google OAuth
- **Custom Template Tags**: Form styling and responsive design helpers
- **Platform-Specific Forms**: Tweet creation, LinkedIn articles, Farcaster casts
- **Validation Patterns**: Domain restrictions, character limits, media handling

### 📈 Operations & Deployment

#### [Deployment Guide](deployment.md)
Railway deployment with PostgreSQL and environment configuration.
- **Railway Setup**: GitHub integration and automatic deployments
- **Database Configuration**: PostgreSQL setup and connection management  
- **Environment Variables**: Production secrets and API key management
- **Scaling Considerations**: Performance optimization and monitoring

#### [Super Admin Setup](super_admin_setup.md)
**WORKING**: Complete guide for accessing the system as super admin.
- **Automatic Creation**: joe@coophive.network and levi@coophive.network
- **Google OAuth Access**: Working authentication via Google accounts
- **Password Reset**: Email-based password reset for super admins
- **Email Configuration**: Database-first email system with Gmail integration

### 📋 Legacy & Reference

#### [UI Modernization](ui_modernization.md)
TaskForge-style UI implementation with modern authentication system.
- **Authentication Templates**: Modern login, registration, OAuth integration
- **Responsive Design**: Mobile-first approach with glassmorphism styling
- **Google OAuth Success**: Complete OAuth implementation with domain restrictions
- **Email System Integration**: Working email verification and password reset

#### [OAuth Success Report](oauth_success_report.md)
Detailed report on successful Google OAuth implementation.
- **Technical Fixes**: Root cause analysis and TaskForge-style solutions
- **User Experience**: Professional error handling and redirect flows
- **Production Ready**: Complete OAuth system with domain restrictions

#### [Twitter App Modification Plan](TWITTER_APP_MODIFICATION_PLAN.MD)
Original comprehensive plan for Twitter/X-Bot integration (now implemented).

### 📊 Sample Data & Workflows

#### [Sample Data Files](/)
- **[in.json](in.json)**: Sample n8n input format for generated tweets
- **[out.json](out.json)**: Sample Django response format for n8n
- **[X_Bot (24).json](X_Bot%20(24).json)**: Complete n8n workflow configuration

## Quick Start Guides

### For Developers
1. Read [Development Guide](development.md) for project setup
2. Review [Configuration Guide](configuration.md) for environment setup  
3. Check [Testing Guide](testing.md) for running tests
4. Explore [Platform Apps Guide](platform_apps_guide.md) for app-specific development

### For System Administrators  
1. Follow [Super Admin Setup](super_admin_setup.md) for initial access
2. Use [Deployment Guide](deployment.md) for production deployment
3. Review [Configuration Guide](configuration.md) for settings management
4. Check [OAuth Success Report](oauth_success_report.md) for authentication status

### For n8n Integration
1. Start with [Twitter/X-Bot Integration Guide](twitter_x_bot_integration_guide.md)
2. Review [n8n Duplicate Check API](n8n_duplicate_check_api.md) for endpoint details
3. Check [n8n Receive Tweets API](n8n_receive_tweets_api.md) for content storage
4. Use sample data files for testing integration

### For API Integration
1. Review [API Documentation](api.md) for all available endpoints
2. Check [Database Models](models.md) for data structure understanding
3. Use [Testing Guide](testing.md) for API testing patterns
4. Follow [Platform Apps Guide](platform_apps_guide.md) for platform-specific APIs

## Documentation Status

### ✅ Complete & Current
- **API Documentation**: All current endpoints documented with examples
- **Database Models**: Complete schema with n8n integration models
- **Twitter/X-Bot Integration**: Comprehensive guide with phase-by-phase implementation
- **Platform Apps**: Detailed guide for all four platform integrations
- **Testing Documentation**: Updated with current test structure and coverage
- **Super Admin System**: Working authentication with multiple access methods

### 🔄 Recently Updated
- **API Documentation**: Added n8n integration endpoints and platform-specific APIs
- **Models Documentation**: Added Twitter n8n models and platform inheritance patterns
- **Testing Guide**: Updated with current test structure and platform coverage
- **Platform Apps Guide**: New comprehensive guide for all platform integrations
- **Twitter Integration Guide**: New complete integration documentation

### 📝 Needs Updates
- **Configuration Guide**: Should be updated with latest settings and features
- **Forms Documentation**: Could be enhanced with more platform-specific examples
- **Deployment Guide**: Could include more production optimization details

## Contributing to Documentation

When updating documentation:

1. **Keep Examples Current**: Ensure code examples match current implementation
2. **Update Cross-References**: Update links when moving or renaming files
3. **Test Instructions**: Verify that setup instructions actually work
4. **Maintain Consistency**: Follow established formatting and structure patterns
5. **Version Information**: Include version information for major changes

## Getting Help

- **Development Issues**: Check [Development Guide](development.md) and [Testing Guide](testing.md)
- **Deployment Problems**: Review [Deployment Guide](deployment.md) and [Configuration Guide](configuration.md)  
- **Authentication Issues**: See [Super Admin Setup](super_admin_setup.md) and [OAuth Success Report](oauth_success_report.md)
- **n8n Integration**: Follow [Twitter/X-Bot Integration Guide](twitter_x_bot_integration_guide.md)
- **API Questions**: Consult [API Documentation](api.md) and [Platform Apps Guide](platform_apps_guide.md)

This documentation provides complete coverage of the CoopHive Social Media Manager system, from basic setup to advanced AI-powered social media automation workflows.
