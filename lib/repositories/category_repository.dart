import '../models/category.dart';
import '../repositories/wallpaper_repository.dart';

/// Contract for fetching wallpaper categories metadata.
abstract interface class ICategoryRepository {
  Future<List<Category>> getCategories();
}

/// Dynamic implementation of [ICategoryRepository] deriving categories directly from discovered wallpapers.
final class LocalCategoryRepository implements ICategoryRepository {
  final IWallpaperRepository wallpaperRepository;

  const LocalCategoryRepository({
    required this.wallpaperRepository,
  });

  @override
  Future<List<Category>> getCategories() async {
    try {
      final wallpapers = await wallpaperRepository.getWallpapers();
      final categoryCounts = <String, int>{};

      for (final w in wallpapers) {
        final cat = w.category.trim();
        if (cat.isNotEmpty) {
          categoryCounts[cat] = (categoryCounts[cat] ?? 0) + 1;
        }
      }

      final categories = <Category>[];
      categoryCounts.forEach((name, count) {
        categories.add(
          Category(
            id: name.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]'), '_'),
            name: name,
            wallpaperCount: count,
            iconName: _iconForCategory(name),
          ),
        );
      });

      categories.sort((a, b) => a.name.compareTo(b.name));
      return categories;
    } catch (_) {
      return const <Category>[];
    }
  }

  String _iconForCategory(String category) {
    switch (category.toLowerCase()) {
      case 'nature':
        return 'landscape';
      case 'abstract':
        return 'palette';
      case 'minimal':
        return 'crop_square';
      case 'city':
      case 'urban':
        return 'location_city';
      case 'space':
        return 'dark_mode';
      case 'anime':
        return 'face';
      default:
        return 'image';
    }
  }
}
