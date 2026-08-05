import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../repositories/wallpaper_repository.dart';
import '../services/asset_service.dart';

/// Provider for the asset service instance.
final assetServiceProvider = Provider<IAssetService>((ref) {
  return AssetBundleService();
});

/// Provider for the local wallpaper repository instance.
final wallpaperRepositoryProvider = Provider<IWallpaperRepository>((ref) {
  final assetService = ref.watch(assetServiceProvider);
  return LocalWallpaperRepository(assetService: assetService);
});

/// FutureProvider that loads and exposes the list of wallpapers.
final wallpapersProvider = FutureProvider<List<Wallpaper>>((ref) async {
  final repository = ref.watch(wallpaperRepositoryProvider);
  return repository.getWallpapers();
});
