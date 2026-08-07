import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/engagement_service.dart';

const String _kLastDailyRatingPromptKey = 'last_daily_rating_prompt_ms';
const int _kOneDayMs = 24 * 60 * 60 * 1000; // 24 hours in milliseconds

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

/// Provider managing the 1-minute daily dwell rating prompt.
/// Triggers native rating popup (iOS App Store & Android Play Store) once user is on the app for >1 minute,
/// capped at 1 time per day.
final dailyDwellRatingProvider = Provider<void>((ref) {
  Timer? timer;

  timer = Timer(const Duration(minutes: 1), () async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final lastPromptMs = prefs.getInt(_kLastDailyRatingPromptKey);
      final nowMs = DateTime.now().millisecondsSinceEpoch;

      if (lastPromptMs == null || (nowMs - lastPromptMs) >= _kOneDayMs) {
        await prefs.setInt(_kLastDailyRatingPromptKey, nowMs);
        final service = ref.read(engagementServiceProvider);
        await service.requestInAppReview();
      }
    } catch (_) {}
  });

  ref.onDispose(() {
    timer?.cancel();
  });
});

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
