import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/category.dart';
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

/// Provider computing structured [Category] models with counts and image previews.
final categoriesProvider = Provider<List<Category>>((ref) {
  final asyncWallpapers = ref.watch(wallpapersProvider);

  return asyncWallpapers.when(
    data: (wallpapers) {
      if (wallpapers.isEmpty) {
        return const <Category>[];
      }

      // Collect unique categories present in the wallpapers
      final Map<String, List<dynamic>> categoryMap = {};
      for (final w in wallpapers) {
        final catName = w.category.trim();
        if (catName.isNotEmpty) {
          final key = catName.toLowerCase();
          categoryMap.putIfAbsent(key, () => []).add(w);
        }
      }

      final List<Category> result = [];
      categoryMap.forEach((key, categoryWallpapers) {
        final displayName = categoryWallpapers.first.category.trim();
        final previewPath = categoryWallpapers.isNotEmpty
            ? categoryWallpapers.first.imagePath
            : null;

        result.add(
          Category(
            id: key,
            name: displayName,
            wallpaperCount: categoryWallpapers.length,
            previewImagePath: previewPath,
            iconName: _getCategoryIconName(displayName),
          ),
        );
      });

      result.sort((a, b) => a.name.compareTo(b.name));
      return result;
    },
    loading: () => const <Category>[],
    error: (error, stack) => const <Category>[],
  );
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
