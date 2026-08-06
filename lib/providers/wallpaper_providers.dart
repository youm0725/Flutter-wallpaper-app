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

/// Family provider that returns a list of wallpapers similar to the given [target].
///
/// Matching logic compares category and tags, excluding the active wallpaper ID.
final similarWallpapersProvider =
    Provider.family<List<Wallpaper>, Wallpaper>((ref, target) {
  final asyncWallpapers = ref.watch(wallpapersProvider);

  return asyncWallpapers.when(
    data: (wallpapers) {
      final targetCategory = target.category.toLowerCase();
      final targetTagsSet = target.tags.map((t) => t.toLowerCase()).toSet();

      return wallpapers.where((w) {
        if (w.id == target.id) return false;

        final isSameCategory = w.category.toLowerCase() == targetCategory;
        final hasSharedTag = w.tags.any(
          (t) => targetTagsSet.contains(t.toLowerCase()),
        );

        return isSameCategory || hasSharedTag;
      }).toList();
    },
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});
