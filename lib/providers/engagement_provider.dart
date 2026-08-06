import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/engagement_service.dart';

/// Provider for [IEngagementService] instance.
final engagementServiceProvider = Provider<IEngagementService>((ref) {
  return LocalEngagementService();
});

/// Requests a native in-app review.
/// Falls back to opening the store page if the review sheet is unavailable.
Future<void> requestAppReview(WidgetRef ref) async {
  final service = ref.read(engagementServiceProvider);
  final triggered = await service.requestInAppReview();
  if (!triggered) {
    // Graceful fallback — open store page directly
    await service.openStoreReviewPage();
  }
}

/// Opens the store review page directly (user-initiated manual action).
Future<void> openStoreReview(WidgetRef ref) async {
  final service = ref.read(engagementServiceProvider);
  await service.openStoreReviewPage();
}

/// Opens a pre-filled feedback email.
Future<bool> openFeedback(WidgetRef ref) async {
  final service = ref.read(engagementServiceProvider);
  return service.openFeedbackEmail();
}
