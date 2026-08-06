/// Centralized content constants for About, Privacy, Terms, and Support screens.
/// Update these values for each release — never scatter them across widgets.
abstract final class AppInfo {
  static const String appName = 'Wallpaper Gallery';
  static const String tagline = 'Premium offline wallpaper collection.';
  static const String description =
      'A curated gallery of high-resolution wallpapers — entirely offline, '
      'no account required, and no data collection. Your device, your gallery.';

  // Support — replace placeholders before store release
  static const String supportEmail = 'support@wallpapergallery.app';
  static const String feedbackUrl = 'https://wallpapergallery.app/feedback';
  static const String websiteUrl = 'https://wallpapergallery.app';
}

/// Privacy Policy content sections.
/// Structured as (heading, body) pairs for easy rendering and future editing.
abstract final class PrivacyContent {
  static const List<({String heading, String body})> sections = [
    (
      heading: 'No Data Collection',
      body:
          'Wallpaper Gallery does not collect, store, transmit, or share any '
          'personal data. We have no servers, no analytics pipelines, and no '
          'user accounts.',
    ),
    (
      heading: 'Fully Offline',
      body:
          'The app works entirely without an internet connection. All wallpaper '
          'images are bundled within the application and stored locally on your '
          'device. No network requests are made.',
    ),
    (
      heading: 'Local Storage Only',
      body:
          'Your favorites, recently viewed history, collections, and preferences '
          'are saved using your device\'s local storage (SharedPreferences). '
          'This data never leaves your device.',
    ),
    (
      heading: 'Permissions',
      body:
          'The app may request access to your Photo Library (iOS) or Media '
          'storage (Android) solely to save wallpapers you choose to download. '
          'These permissions are optional and only activated on your explicit '
          'request.',
    ),
    (
      heading: 'Third-Party Packages',
      body:
          'Wallpaper Gallery uses open-source Flutter packages. These packages '
          'do not send data to third parties. A full list is available on the '
          'Open Source Licenses screen.',
    ),
    (
      heading: 'Children\'s Privacy',
      body:
          'This app does not target children under 13 and does not knowingly '
          'collect data from any users of any age.',
    ),
    (
      heading: 'Contact',
      body:
          'If you have any privacy questions, reach us at ${AppInfo.supportEmail}.',
    ),
  ];
}

/// Terms & Conditions content sections.
abstract final class TermsContent {
  static const List<({String heading, String body})> sections = [
    (
      heading: 'Acceptance of Terms',
      body:
          'By installing or using Wallpaper Gallery, you agree to these terms. '
          'If you do not agree, please uninstall the application.',
    ),
    (
      heading: 'License to Use',
      body:
          'Wallpaper Gallery grants you a personal, non-exclusive, '
          'non-transferable license to use the application on your devices.',
    ),
    (
      heading: 'Wallpaper Content',
      body:
          'All wallpaper images included in the app are either licensed for '
          'distribution, created for this application, or sourced from '
          'permissive-license repositories. The images are provided for '
          'personal, non-commercial use.',
    ),
    (
      heading: 'Prohibited Use',
      body:
          'You may not: redistribute the wallpaper images commercially, '
          'reverse-engineer the application, or use the app in any way that '
          'violates applicable laws.',
    ),
    (
      heading: 'Disclaimer',
      body:
          'The application is provided "as is" without warranty of any kind. '
          'We do not guarantee uninterrupted or error-free operation.',
    ),
    (
      heading: 'Changes to Terms',
      body:
          'We may update these terms from time to time. Continued use of the '
          'app after changes constitutes acceptance of the revised terms.',
    ),
    (
      heading: 'Contact',
      body: 'For any questions, contact us at ${AppInfo.supportEmail}.',
    ),
  ];
}
