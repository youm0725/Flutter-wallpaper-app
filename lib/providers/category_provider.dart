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

/// Standard category taxonomy defined for the application.
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
      return kStandardCategories.map((catName) {
        final matchingWallpapers = wallpapers.where(
          (w) => w.category.toLowerCase() == catName.toLowerCase(),
        ).toList();

        final previewPath = matchingWallpapers.isNotEmpty
            ? matchingWallpapers.first.imagePath
            : null;

        return Category(
          id: catName.toLowerCase(),
          name: catName,
          wallpaperCount: matchingWallpapers.length,
          previewImagePath: previewPath,
          iconName: _getCategoryIconName(catName),
        );
      }).toList();
    },
    loading: () => kStandardCategories
        .map((name) => Category(id: name.toLowerCase(), name: name))
        .toList(),
    error: (error, stack) => kStandardCategories
        .map((name) => Category(id: name.toLowerCase(), name: name))
        .toList(),
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
