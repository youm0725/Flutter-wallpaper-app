import '../models/wallpaper.dart';

/// Contract for offline wallpaper search operations.
abstract interface class ISearchService {
  List<Wallpaper> searchWallpapers(List<Wallpaper> wallpapers, String query);
}

/// Production implementation of [ISearchService] for instant offline search.
final class LocalSearchService implements ISearchService {
  const LocalSearchService();

  @override
  List<Wallpaper> searchWallpapers(List<Wallpaper> wallpapers, String query) {
    final cleanedQuery = query.trim().toLowerCase();

    if (cleanedQuery.isEmpty) {
      return const <Wallpaper>[];
    }

    return wallpapers.where((wallpaper) {
      final matchesTitle = wallpaper.title.toLowerCase().contains(cleanedQuery);
      final matchesCategory =
          wallpaper.category.toLowerCase().contains(cleanedQuery);
      final matchesTags = wallpaper.tags.any(
        (tag) => tag.toLowerCase().contains(cleanedQuery),
      );

      return matchesTitle || matchesCategory || matchesTags;
    }).toList(growable: false);
  }
}
