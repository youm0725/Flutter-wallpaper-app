import 'dart:io';
import 'package:in_app_review/in_app_review.dart';
import 'package:url_launcher/url_launcher.dart';
import '../core/constants/store_constants.dart';

/// Service interface for app engagement actions: rating, feedback.
abstract interface class IEngagementService {
  /// Requests an in-app review. Returns true if the request was dispatched.
  /// On iOS this shows the native SKStoreReviewController.
  /// On Android this shows the Google Play in-app review sheet.
  /// May silently no-op if the platform rate-limits the request.
  Future<bool> requestInAppReview();

  /// Opens the store review page as a fallback when [requestInAppReview] is
  /// unavailable or after repeated in-app prompts.
  Future<bool> openStoreReviewPage();

  /// Opens a mailto: intent pre-filled with feedback subject and recipient.
  Future<bool> openFeedbackEmail();
}

/// Production implementation of [IEngagementService] using [InAppReview] and [url_launcher].
final class LocalEngagementService implements IEngagementService {
  final InAppReview _review = InAppReview.instance;

  LocalEngagementService();

  @override
  Future<bool> requestInAppReview() async {
    try {
      if (await _review.isAvailable()) {
        await _review.requestReview();
        return true;
      }
      await _review.openStoreListing();
      return true;
    } catch (_) {
      return openStoreReviewPage();
    }
  }

  @override
  Future<bool> openStoreReviewPage() async {
    try {
      final storeUrl = Platform.isIOS
          ? StoreConstants.appStoreReviewUrl
          : StoreConstants.playStoreReviewUrl;
      final uri = Uri.parse(storeUrl);
      if (!await canLaunchUrl(uri)) return false;
      await launchUrl(uri, mode: LaunchMode.externalApplication);
      return true;
    } catch (_) {
      return false;
    }
  }

  @override
  Future<bool> openFeedbackEmail() async {
    try {
      final subject = Uri.encodeComponent(StoreConstants.feedbackSubject);
      final uri = Uri.parse(
        'mailto:${StoreConstants.supportEmail}?subject=$subject',
      );
      if (!await canLaunchUrl(uri)) return false;
      await launchUrl(uri);
      return true;
    } catch (_) {
      return false;
    }
  }
}
