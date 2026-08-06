import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../services/share_service.dart';

/// Provider for [IShareService] instance.
final shareServiceProvider = Provider<IShareService>((ref) {
  return const LocalShareService();
});

/// Shares a wallpaper using native platform share sheet.
Future<bool> shareWallpaper(WidgetRef ref, Wallpaper wallpaper) async {
  final service = ref.read(shareServiceProvider);
  return service.shareWallpaper(wallpaper);
}

/// Shares the wallpaper app using native platform share sheet.
Future<bool> shareApp(WidgetRef ref) async {
  final service = ref.read(shareServiceProvider);
  return service.shareApp();
}
