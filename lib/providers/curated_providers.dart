import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/collection.dart';
import '../models/wallpaper.dart';
import '../repositories/collection_repository.dart';
import '../services/daily_wallpaper_service.dart';
import 'wallpaper_providers.dart';

/// Provider for [ICollectionRepository] instance.
final collectionRepositoryProvider = Provider<ICollectionRepository>((ref) {
  final assetService = ref.watch(assetServiceProvider);
  return LocalCollectionRepository(assetService: assetService);
});

/// FutureProvider that loads and exposes curated collections.
final collectionsProvider = FutureProvider<List<Collection>>((ref) async {
  final repository = ref.watch(collectionRepositoryProvider);
  return repository.getCollections();
});

/// Provider for [IDailyWallpaperService] instance.
final dailyWallpaperServiceProvider = Provider<IDailyWallpaperService>((ref) {
  return const DailyWallpaperService();
});

/// Provider computing Editor's Picks / Featured wallpapers list.
final featuredWallpapersProvider = Provider<List<Wallpaper>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);

  return asyncWallpapers.when(
    data: (wallpapers) => wallpapers.where((w) => w.isFeatured).toList(),
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});

/// Provider computing the Wallpaper of the Day for current date.
final dailyWallpaperProvider = Provider<Wallpaper?>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);
  final dailyService = ref.watch(dailyWallpaperServiceProvider);

  return asyncWallpapers.when(
    data: (wallpapers) => dailyService.getDailyWallpaper(wallpapers),
    loading: () => null,
    error: (error, stack) => null,
  );
});
