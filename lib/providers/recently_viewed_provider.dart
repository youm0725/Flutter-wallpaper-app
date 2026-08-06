import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../repositories/recently_viewed_repository.dart';
import 'wallpaper_providers.dart';

/// Provider for [IRecentlyViewedRepository] instance.
final recentlyViewedRepositoryProvider =
    Provider<IRecentlyViewedRepository>((ref) {
  return const LocalRecentlyViewedRepository();
});

/// AsyncNotifier managing recently viewed wallpaper IDs history.
class RecentlyViewedNotifier extends AsyncNotifier<List<String>> {
  @override
  Future<List<String>> build() async {
    final repository = ref.watch(recentlyViewedRepositoryProvider);
    return repository.getRecentlyViewedIds();
  }

  Future<void> addWallpaperView(String wallpaperId) async {
    final current = state.value ?? const <String>[];
    final repository = ref.read(recentlyViewedRepositoryProvider);

    final updated = <String>[
      wallpaperId,
      ...current.where((id) => id != wallpaperId),
    ].take(20).toList();

    state = AsyncData(updated);
    await repository.addRecentlyViewedId(wallpaperId);
  }

  Future<void> clearHistory() async {
    state = const AsyncData(<String>[]);
    final repository = ref.read(recentlyViewedRepositoryProvider);
    await repository.clearRecentlyViewed();
  }
}

/// Provider for active list of recently viewed wallpaper IDs.
final recentlyViewedNotifierProvider =
    AsyncNotifierProvider<RecentlyViewedNotifier, List<String>>(
  RecentlyViewedNotifier.new,
);

/// Provider yielding ordered list of recently viewed [Wallpaper] objects.
final recentlyViewedWallpapersProvider = Provider<List<Wallpaper>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);
  final asyncRecentIds = ref.watch(recentlyViewedNotifierProvider);

  final recentIds = asyncRecentIds.value ?? const <String>[];
  if (recentIds.isEmpty) return const <Wallpaper>[];

  return asyncWallpapers.when(
    data: (wallpapers) {
      final map = {for (final w in wallpapers) w.id: w};
      final result = <Wallpaper>[];
      for (final id in recentIds) {
        if (map.containsKey(id)) {
          result.add(map[id]!);
        }
      }
      return result;
    },
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});
