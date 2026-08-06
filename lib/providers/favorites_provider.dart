import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/wallpaper.dart';
import '../repositories/favorites_repository.dart';
import 'wallpaper_providers.dart';

/// Provider for [IFavoritesRepository] instance.
final favoritesRepositoryProvider = Provider<IFavoritesRepository>((ref) {
  return const LocalFavoritesRepository();
});

/// AsyncNotifier managing active set of favorited wallpaper IDs.
class FavoritesNotifier extends AsyncNotifier<Set<String>> {
  @override
  Future<Set<String>> build() async {
    final repository = ref.watch(favoritesRepositoryProvider);
    final ids = await repository.getFavoriteIds();
    return ids.toSet();
  }

  /// Toggles favorite status for a given wallpaper ID.
  ///
  /// Returns `true` if item is now favorited, or `false` if removed.
  Future<bool> toggleFavorite(String wallpaperId) async {
    final currentSet = state.value ?? const <String>{};
    final repository = ref.read(favoritesRepositoryProvider);

    final isFav = currentSet.contains(wallpaperId);
    final updatedSet = Set<String>.from(currentSet);

    if (isFav) {
      updatedSet.remove(wallpaperId);
      state = AsyncData(updatedSet);
      await repository.removeFavorite(wallpaperId);
      return false;
    } else {
      updatedSet.add(wallpaperId);
      state = AsyncData(updatedSet);
      await repository.addFavorite(wallpaperId);
      return true;
    }
  }

  /// Checks if a wallpaper ID is currently favorited.
  bool isFavorite(String wallpaperId) {
    return state.value?.contains(wallpaperId) ?? false;
  }
}

/// Provider for active favorited wallpaper IDs set.
final favoritesNotifierProvider =
    AsyncNotifierProvider<FavoritesNotifier, Set<String>>(
  FavoritesNotifier.new,
);

/// Provider computing full list of favorited [Wallpaper] objects.
final favoriteWallpapersProvider = Provider<List<Wallpaper>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);
  final asyncFavoriteIds = ref.watch(favoritesNotifierProvider);

  final favoriteIds = asyncFavoriteIds.value ?? const <String>{};

  return asyncWallpapers.when(
    data: (wallpapers) {
      return wallpapers.where((w) => favoriteIds.contains(w.id)).toList();
    },
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});
