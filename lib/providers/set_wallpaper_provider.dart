import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../services/wallpaper_service.dart';

/// Provider for [IWallpaperService] instance.
final wallpaperServiceProvider = Provider<IWallpaperService>((ref) {
  return const LocalWallpaperService();
});

/// Notifier tracking active setting wallpaper IDs set.
class ActiveSettingWallpaperNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => const <String>{};

  void startSetting(String wallpaperId) {
    state = {...state, wallpaperId};
  }

  void stopSetting(String wallpaperId) {
    state = state.where((id) => id != wallpaperId).toSet();
  }

  bool isSetting(String wallpaperId) {
    return state.contains(wallpaperId);
  }
}

/// Provider for set of currently setting wallpaper IDs.
final activeSettingWallpaperProvider =
    NotifierProvider<ActiveSettingWallpaperNotifier, Set<String>>(
  ActiveSettingWallpaperNotifier.new,
);

/// Controller method executing wallpaper application for Android/iOS.
Future<bool> applyWallpaper(
  WidgetRef ref,
  Wallpaper wallpaper,
  WallpaperTarget target,
) async {
  final service = ref.read(wallpaperServiceProvider);
  final settingNotifier = ref.read(activeSettingWallpaperProvider.notifier);

  settingNotifier.startSetting(wallpaper.id);

  try {
    final success = await service.setWallpaper(wallpaper, target);
    settingNotifier.stopSetting(wallpaper.id);
    return success;
  } catch (_) {
    settingNotifier.stopSetting(wallpaper.id);
    return false;
  }
}
