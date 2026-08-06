import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/wallpaper.dart';
import '../services/search_service.dart';
import 'wallpaper_providers.dart';

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
