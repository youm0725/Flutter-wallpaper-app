import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/wallpaper.dart';
import '../services/search_service.dart';
import 'category_provider.dart';
import 'wallpaper_providers.dart';

/// Types of autocomplete search suggestions.
enum SuggestionType {
  category,
  tag,
  wallpaper,
}

/// Domain model for an autocomplete search suggestion.
class SearchSuggestion {
  final String title;
  final String subtitle;
  final SuggestionType type;
  final String query;

  const SearchSuggestion({
    required this.title,
    required this.subtitle,
    required this.type,
    required this.query,
  });
}

/// Provider for [ISearchService] instance.
final searchServiceProvider = Provider<ISearchService>((ref) {
  return const LocalSearchService();
});

/// Notifier managing active search query text.
class SearchQueryNotifier extends Notifier<String> {
  @override
  String build() => '';

  void setQuery(String query) {
    state = query;
  }

  void clearQuery() {
    state = '';
  }
}

/// Provider for active search query string.
final searchQueryProvider =
    NotifierProvider<SearchQueryNotifier, String>(SearchQueryNotifier.new);

/// Notifier managing local recent search query history persisted via [SharedPreferences].
class RecentSearchesNotifier extends AsyncNotifier<List<String>> {
  static const String _key = 'recent_searches_key';
  static const int _maxItems = 8;

  @override
  Future<List<String>> build() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_key) ?? const <String>[];
  }

  Future<void> addQuery(String query) async {
    final trimmed = query.trim();
    if (trimmed.isEmpty) return;

    final current = state.value ?? <String>[];
    final updated = <String>[
      trimmed,
      ...current.where((q) => q.toLowerCase() != trimmed.toLowerCase()),
    ].take(_maxItems).toList();

    state = AsyncData(updated);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_key, updated);
  }

  Future<void> removeQuery(String query) async {
    final current = state.value ?? <String>[];
    final updated = current.where((q) => q != query).toList();

    state = AsyncData(updated);

    final prefs = await SharedPreferences.getInstance();
    await prefs.setStringList(_key, updated);
  }

  Future<void> clearAll() async {
    state = const AsyncData(<String>[]);
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_key);
  }
}

/// Provider for recent searches history list.
final recentSearchesProvider =
    AsyncNotifierProvider<RecentSearchesNotifier, List<String>>(
  RecentSearchesNotifier.new,
);

/// Provider yielding filtered search results based on active query.
final searchResultsProvider = Provider<List<Wallpaper>>((ref) {
  final query = ref.watch(searchQueryProvider);
  final asyncWallpapers = ref.watch(wallpapersProvider);
  final searchService = ref.watch(searchServiceProvider);

  return asyncWallpapers.when(
    data: (wallpapers) => searchService.searchWallpapers(wallpapers, query),
    loading: () => const <Wallpaper>[],
    error: (error, stack) => const <Wallpaper>[],
  );
});

/// Provider computing instant search autocomplete suggestions for query text.
final searchSuggestionsProvider = Provider<List<SearchSuggestion>>((ref) {
  final rawQuery = ref.watch(searchQueryProvider).trim().toLowerCase();
  if (rawQuery.isEmpty) return const <SearchSuggestion>[];

  final suggestions = <SearchSuggestion>[];

  // 1. Match categories
  for (final catName in kStandardCategories) {
    if (catName.toLowerCase().contains(rawQuery)) {
      suggestions.add(
        SearchSuggestion(
          title: catName,
          subtitle: 'Category',
          type: SuggestionType.category,
          query: catName,
        ),
      );
    }
  }

  // 2. Match tags
  final tagsMap = ref.watch(allTagsProvider);
  for (final entry in tagsMap.entries) {
    final tag = entry.key;
    if (tag.contains(rawQuery)) {
      suggestions.add(
        SearchSuggestion(
          title: '#$tag',
          subtitle: 'Tag (${entry.value} wallpapers)',
          type: SuggestionType.tag,
          query: tag,
        ),
      );
    }
  }

  // 3. Match wallpaper titles
  final asyncWallpapers = ref.watch(wallpapersProvider);
  asyncWallpapers.whenData((wallpapers) {
    for (final w in wallpapers) {
      if (w.title.toLowerCase().contains(rawQuery)) {
        suggestions.add(
          SearchSuggestion(
            title: w.title,
            subtitle: 'Wallpaper in ${w.category}',
            type: SuggestionType.wallpaper,
            query: w.title,
          ),
        );
      }
    }
  });

  return suggestions.take(8).toList();
});
