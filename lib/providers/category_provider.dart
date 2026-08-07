import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/category.dart';
import '../repositories/category_repository.dart';
import 'wallpaper_providers.dart';

/// Notifier managing the currently selected single category filter string.
class SelectedCategoryNotifier extends Notifier<String> {
  @override
  String build() => 'All';

  void selectCategory(String category) {
    state = category;
  }
}

/// Provider for the currently selected category name.
final selectedCategoryProvider =
    NotifierProvider<SelectedCategoryNotifier, String>(
  SelectedCategoryNotifier.new,
);

/// Notifier managing multi-tag filter selections.
class SelectedTagsNotifier extends Notifier<Set<String>> {
  @override
  Set<String> build() => const <String>{};

  void toggleTag(String tag) {
    final lowercaseTag = tag.toLowerCase();
    if (state.contains(lowercaseTag)) {
      state = Set<String>.from(state)..remove(lowercaseTag);
    } else {
      state = Set<String>.from(state)..add(lowercaseTag);
    }
  }

  void clearTags() {
    state = const <String>{};
  }
}

/// Provider for multi-tag filtering selection set.
final selectedTagsProvider =
    NotifierProvider<SelectedTagsNotifier, Set<String>>(
  SelectedTagsNotifier.new,
);

/// Standard category taxonomy defined for the application fallback.
const List<String> kStandardCategories = <String>[
  'Nature',
  'Abstract',
  'AMOLED',
  'Cars',
  'Gaming',
  'Minimal',
  'Space',
  'Anime',
  'Architecture',
  'Technology',
];

/// Provider for [ICategoryRepository] instance.
final categoryRepositoryProvider = Provider<ICategoryRepository>((ref) {
  final wallpaperRepo = ref.watch(wallpaperRepositoryProvider);
  return LocalCategoryRepository(wallpaperRepository: wallpaperRepo);
});

/// FutureProvider loading raw category definitions from assets/metadata/categories.json.
final rawCategoriesProvider = FutureProvider<List<Category>>((ref) async {
  final repository = ref.watch(categoryRepositoryProvider);
  return await repository.getCategories();
});

/// Provider computing structured [Category] models combining categories.json and wallpapers.
final categoriesProvider = Provider<List<Category>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);
  final asyncRawCategories = ref.watch(rawCategoriesProvider);

  final wallpapers = asyncWallpapers.value ?? const [];
  final rawCategories = asyncRawCategories.value ?? const [];

  if (wallpapers.isEmpty && rawCategories.isEmpty) {
    return const <Category>[];
  }

  // 1. Group wallpapers by category key (lowercase)
  final Map<String, List<dynamic>> wallpapersByCat = {};
  for (final w in wallpapers) {
    final catName = w.category.trim();
    if (catName.isNotEmpty) {
      final key = catName.toLowerCase();
      wallpapersByCat.putIfAbsent(key, () => []).add(w);
    }
  }

  // 2. Build Category objects starting from metadata rawCategories
  final Map<String, Category> resultCategories = {};
  for (final cat in rawCategories) {
    final key = cat.id.toLowerCase();
    final matchingWallpapers = wallpapersByCat[key] ?? const [];
    final previewPath = matchingWallpapers.isNotEmpty
        ? matchingWallpapers.first.imagePath
        : null;

    resultCategories[key] = Category(
      id: key,
      name: cat.name,
      description: cat.description,
      wallpaperCount: matchingWallpapers.length,
      previewImagePath: previewPath,
      iconName: cat.iconName.isNotEmpty ? cat.iconName : _getCategoryIconName(cat.name),
    );
  }

  // 3. Add any categories present in wallpapers but missing from rawCategories
  wallpapersByCat.forEach((key, categoryWallpapers) {
    if (!resultCategories.containsKey(key)) {
      final displayName = categoryWallpapers.first.category.trim();
      final previewPath = categoryWallpapers.isNotEmpty
          ? categoryWallpapers.first.imagePath
          : null;

      resultCategories[key] = Category(
        id: key,
        name: displayName,
        wallpaperCount: categoryWallpapers.length,
        previewImagePath: previewPath,
        iconName: _getCategoryIconName(displayName),
      );
    }
  });

  final List<Category> resultList = resultCategories.values.toList();
  resultList.sort((a, b) => a.name.compareTo(b.name));
  return resultList;
});

/// Provider computing all unique tags and their item counts across offline wallpapers.
final allTagsProvider = Provider<Map<String, int>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);

  return asyncWallpapers.when(
    data: (wallpapers) {
      final map = <String, int>{};
      for (final wallpaper in wallpapers) {
        for (final tag in wallpaper.tags) {
          final normalized = tag.toLowerCase();
          map[normalized] = (map[normalized] ?? 0) + 1;
        }
      }
      return map;
    },
    loading: () => const <String, int>{},
    error: (error, stack) => const <String, int>{},
  );
});

String _getCategoryIconName(String categoryName) {
  switch (categoryName.toLowerCase()) {
    case 'nature':
      return 'forest';
    case 'abstract':
      return 'palette';
    case 'amoled':
      return 'dark_mode';
    case 'cars':
      return 'directions_car';
    case 'gaming':
      return 'sports_esports';
    case 'minimal':
      return 'crop_square';
    case 'space':
      return 'public';
    case 'anime':
      return 'face';
    case 'architecture':
      return 'location_city';
    case 'technology':
      return 'memory';
    default:
      return 'category';
  }
}
