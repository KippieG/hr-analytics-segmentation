# Leafy Quest - Quit Weed Journey App

![Swift](https://img.shields.io/badge/Swift-5.9-orange.svg)
![iOS](https://img.shields.io/badge/iOS-17.0+-blue.svg)
![SwiftUI](https://img.shields.io/badge/SwiftUI-Latest-green.svg)

**Leafy Quest** is a comprehensive, gamified iOS app designed to help people quit smoking weed. Built with SwiftUI, featuring RevenueCat subscriptions and Google AdMob monetization.

## 🌟 Features

### Core Features
- ✅ **Interactive Onboarding** - Beautiful multi-page welcome flow
- 📋 **Comprehensive Quiz System** - 11-question assessment to understand user profile
- 📊 **Progress Tracking** - Real-time streak counter and statistics
- 💰 **Money Saved Calculator** - Track financial savings from quitting
- 🏆 **Achievement System** - Unlock badges for milestones
- 📝 **Daily Journal** - Log mood, cravings, triggers, and strategies
- 🎯 **Health Milestones** - Track physical and mental improvements
- 💪 **Coping Strategies** - Emergency SOS tools and techniques
- 🎨 **Beautiful UI** - Modern design with gradients and animations

### Premium Features
- 🚫 **Ad-Free Experience**
- 📈 **Advanced Statistics**
- 🎯 **Custom Goals**
- 💡 **Personalized Daily Tips**
- 📤 **Data Export** (PDF, CSV, JSON)
- 🌙 **Dark Mode & Themes**
- 📱 **Home Screen Widgets**

### Monetization
- 💳 **RevenueCat Integration** - Subscription management
- 📱 **Google AdMob** - Banner, Interstitial, and Rewarded ads
- 🎁 **Free Trial** - 7-day trial for premium features
- 💎 **Multiple Plans** - Weekly, Monthly, Annual, Lifetime

## 📱 Screenshots

*Coming soon*

## 🏗 Architecture

### File Structure
```
LeafyQuest/
├── LeafyQuestApp.swift          # Main app entry point
├── Models.swift                  # Data models and enums
├── SubscriptionManager.swift     # RevenueCat integration
├── OnboardingView.swift          # Welcome flow
├── QuizView.swift                # User assessment quiz
├── MainTabView.swift             # Main navigation
├── ProgressView.swift            # Progress tracking
├── AchievementsView.swift        # Gamification
├── JournalView.swift             # Daily logging
├── SettingsView.swift            # App settings
├── PaywallView.swift             # Premium subscription
├── AdBannerView.swift            # AdMob integration
└── Info.plist                    # App configuration
```

### Key Components

#### AppState
Central state management for:
- User profile
- Quit date tracking
- Streak calculation
- Achievement unlocking
- Progress persistence

#### SubscriptionManager
Handles all premium features:
- RevenueCat SDK integration
- Package fetching
- Purchase processing
- Restore purchases
- Feature access control

#### Models
```swift
- UserProfile
- QuizQuestion & QuizAnswer
- Achievement
- DailyLog
- HealthMilestone
- MotivationalQuote
- CopingStrategy
```

## 🚀 Getting Started

### Prerequisites
- Xcode 15.0+
- iOS 17.0+
- CocoaPods or Swift Package Manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/leafy-quest.git
cd leafy-quest
```

2. **Install Dependencies**

Using Swift Package Manager (recommended):
- RevenueCat SDK: `https://github.com/RevenueCat/purchases-ios.git`
- Google Mobile Ads: `https://github.com/googleads/swift-package-manager-google-mobile-ads.git`

Or using CocoaPods:
```bash
pod install
```

3. **Configure RevenueCat**
- Sign up at [RevenueCat](https://www.revenuecat.com/)
- Create a new project
- Add your iOS app
- Replace `YOUR_REVENUECAT_API_KEY` in `LeafyQuestApp.swift`

4. **Configure Google AdMob**
- Sign up at [Google AdMob](https://admob.google.com/)
- Create a new app
- Get your App ID
- Replace test ad unit IDs in `AdBannerView.swift`
- Update `GADApplicationIdentifier` in `Info.plist`

5. **Run the app**
```bash
open LeafyQuest.xcodeproj
```
Press ⌘R to build and run

## 🔧 Configuration

### RevenueCat Setup

1. Create products in App Store Connect:
   - Weekly subscription
   - Monthly subscription
   - Annual subscription
   - Lifetime purchase (non-consumable)

2. Configure offerings in RevenueCat dashboard

3. Add entitlement ID: `premium`

### AdMob Setup

1. Create ad units:
   - Banner Ad
   - Interstitial Ad
   - Rewarded Ad

2. Update ad unit IDs in code (replace test IDs):
```swift
// Banner: ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY
// Interstitial: ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY
// Rewarded: ca-app-pub-XXXXXXXXXXXXXXXX/YYYYYYYYYY
```

3. Add SKAdNetwork IDs to Info.plist (already included)

## 📊 Data Persistence

The app uses UserDefaults for data persistence:
- User profile and quiz answers
- Quit date and streak
- Achievements
- Daily journal entries
- Settings and preferences

For production, consider upgrading to:
- Core Data for complex queries
- CloudKit for cross-device sync
- Keychain for sensitive data

## 🎨 Design System

### Colors
- **Primary**: Green (health, success)
- **Secondary**: Blue (calm, trust)
- **Accent**: Purple, Orange, Yellow (achievements)
- **Alert**: Red (warnings)

### Typography
- **Headings**: System Bold
- **Body**: System Regular
- **Captions**: System Regular (smaller)

### Components
- Rounded corners (12-16px)
- Subtle shadows
- Gradient backgrounds
- Smooth animations

## 🧪 Testing

### Test Accounts
- **RevenueCat**: Use sandbox mode
- **AdMob**: Test ad units included

### Debug Features
- Skip quiz option
- Reset progress
- View all achievements
- Manual streak adjustment

## 📈 Analytics

Recommended analytics to track:
- Daily active users (DAU)
- Retention rates (D1, D7, D30)
- Average session length
- Quiz completion rate
- Journal entry frequency
- Achievement unlock rates
- Subscription conversion
- Ad impressions & clicks
- In-app purchase revenue

Consider integrating:
- Firebase Analytics
- Mixpanel
- Amplitude

## 🔐 Privacy & Security

- **No personal health data** stored on servers
- **Local-first** architecture
- **Transparent data usage**
- GDPR compliant
- ATT (App Tracking Transparency) support

## 📦 Dependencies

```swift
dependencies: [
    .package(url: "https://github.com/RevenueCat/purchases-ios.git", from: "4.0.0"),
    .package(url: "https://github.com/googleads/swift-package-manager-google-mobile-ads.git", from: "11.0.0")
]
```

## 🚀 Deployment

### App Store Submission

1. **Prepare assets**:
   - App icon (1024x1024)
   - Screenshots (all sizes)
   - Preview video (optional)

2. **Update version**:
   - Increment `CFBundleShortVersionString`
   - Increment `CFBundleVersion`

3. **Archive and upload**:
   - Product → Archive
   - Distribute to App Store Connect

4. **App Review Information**:
   - Test account (if needed)
   - Review notes
   - Demo video

### App Store Optimization (ASO)

**Title**: Leafy Quest: Quit Weed Tracker

**Subtitle**: Stop Smoking & Track Progress

**Keywords**: quit weed, stop smoking, sobriety tracker, addiction recovery, quit cannabis, health tracker, wellness app, habit tracker

**Description**:
```
Transform your life with Leafy Quest, the #1 app for quitting weed!

🌱 WHY LEAFY QUEST?
• Beautiful, gamified interface makes quitting fun
• Track your progress with detailed statistics
• Unlock achievements as you reach milestones
• Daily journal to log mood and cravings
• Emergency SOS tools when you need support
• See real-time money saved
• Health timeline showing improvements

🎯 FEATURES
✓ Personalized quit plan based on your profile
✓ Streak counter and progress tracking
✓ Achievement badges and rewards
✓ Daily motivational quotes
✓ Coping strategies database
✓ Mood and craving tracker
✓ Money saved calculator
✓ Health milestone timeline

💎 PREMIUM
• Remove all ads
• Advanced analytics
• Custom goals
• Data export
• Exclusive themes
• Priority support

Join thousands who've successfully quit with Leafy Quest!

Download now and start your journey to freedom. 🚀

---
Note: This app is not a substitute for professional medical advice.
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- RevenueCat for subscription management
- Google AdMob for monetization
- SF Symbols for icons
- Community feedback and support

## 📞 Support

- **Email**: support@leafyquest.com
- **Website**: https://leafyquest.com
- **Twitter**: @LeafyQuestApp

## 🗺 Roadmap

### Version 1.1
- [ ] Apple Watch companion app
- [ ] Home screen widgets
- [ ] Siri shortcuts integration
- [ ] Share progress with friends

### Version 1.2
- [ ] Community features
- [ ] Support groups
- [ ] Expert content library
- [ ] Guided meditations

### Version 2.0
- [ ] AI-powered personalized coaching
- [ ] Predictive craving alerts
- [ ] Social challenges
- [ ] Therapy integration

---

Made with ❤️ for everyone on their quit journey

**Remember**: Every day smoke-free is a victory! 🌟
