import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../repositories/download_repository.dart';
import 'engagement_provider.dart';

/// Result status of a wallpaper download attempt.
enum DownloadResult {
  success,
  permissionDenied,
  error,
}

/// Provider for [IDownloadRepository] instance.
final downloadRepositoryProvider = Provider<IDownloadRepository>((ref) {
  return const LocalDownloadRepository();
});

/// Notifier tracking active downloading wallpaper IDs set.
class ActiveDownloadsNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => const <String>{};

  void startDownload(String wallpaperId) {
    state = {...state, wallpaperId};
  }

  void stopDownload(String wallpaperId) {
    state = state.where((id) => id != wallpaperId).toSet();
  }

  bool isDownloading(String wallpaperId) {
    return state.contains(wallpaperId);
  }
}

/// Provider for set of currently downloading wallpaper IDs.
final activeDownloadsProvider =
    NotifierProvider<ActiveDownloadsNotifier, Set<String>>(
  ActiveDownloadsNotifier.new,
);

/// Controller method executing wallpaper download with permission handling.
Future<DownloadResult> downloadWallpaper(
  WidgetRef ref,
  Wallpaper wallpaper,
) async {
  final repository = ref.read(downloadRepositoryProvider);
  final downloadsNotifier = ref.read(activeDownloadsProvider.notifier);

  downloadsNotifier.startDownload(wallpaper.id);

  try {
    final hasAccess = await repository.hasStoragePermission();
    if (!hasAccess) {
      final granted = await repository.requestStoragePermission();
      if (!granted) {
        downloadsNotifier.stopDownload(wallpaper.id);
        return DownloadResult.permissionDenied;
      }
    }

    final success = await repository.saveWallpaperToGallery(wallpaper);
    downloadsNotifier.stopDownload(wallpaper.id);

    if (success) {
      // Trigger native in-app rating popup for iOS and Play Store
      await requestAppReview(ref);
    }

    return success ? DownloadResult.success : DownloadResult.error;
  } catch (_) {
    downloadsNotifier.stopDownload(wallpaper.id);
    return DownloadResult.error;
  }
}
