import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../models/wallpaper.dart';
import '../../providers/search_providers.dart';
import '../../widgets/widgets.dart';

/// Dedicated Search Screen for instant offline wallpaper discovery.
class SearchScreen extends ConsumerStatefulWidget {
  const SearchScreen({super.key});

  @override
  ConsumerState<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends ConsumerState<SearchScreen> {
  late final TextEditingController _controller;
  late final FocusNode _focusNode;

  static const List<String> _popularSuggestions = <String>[
    'nature',
    'amoled',
    'abstract',
    'space',
    'cars',
    'minimal',
    'anime',
    'forest',
  ];

  @override
  void initState() {
    super.initState();
    final initialQuery = ref.read(searchQueryProvider);
    _controller = TextEditingController(text: initialQuery);
    _focusNode = FocusNode();
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _onQueryChanged(String text) {
    ref.read(searchQueryProvider.notifier).setQuery(text);
  }

  void _submitSearch(String query) {
    if (query.trim().isNotEmpty) {
      ref.read(recentSearchesProvider.notifier).addQuery(query);
      _focusNode.unfocus();
    }
  }

  void _selectQuery(String query) {
    _controller.text = query;
    _controller.selection = TextSelection.fromPosition(
      TextPosition(offset: query.length),
    );
    ref.read(searchQueryProvider.notifier).setQuery(query);
    ref.read(recentSearchesProvider.notifier).addQuery(query);
    _focusNode.unfocus();
  }

  void _clearQuery() {
    _controller.clear();
    ref.read(searchQueryProvider.notifier).clearQuery();
    _focusNode.requestFocus();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final activeQuery = ref.watch(searchQueryProvider);
    final searchResults = ref.watch(searchResultsProvider);
    final asyncRecentSearches = ref.watch(recentSearchesProvider);
    final suggestions = ref.watch(searchSuggestionsProvider);

    return Scaffold(
      appBar: AppBar(
        automaticallyImplyLeading: false,
        titleSpacing: AppSizes.p8,
        title: Row(
          children: [
            IconButton(
              icon: const Icon(Icons.arrow_back_rounded),
              onPressed: () => context.pop(),
              tooltip: 'Back',
            ),
            Expanded(
              child: Container(
                height: 48.0,
                decoration: BoxDecoration(
                  color: isDark
                      ? theme.colorScheme.surfaceContainerHighest
                      : theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.6),
                  borderRadius: BorderRadius.circular(AppSizes.radiusMd),
                  border: Border.all(
                    color: theme.colorScheme.outline.withValues(alpha: 0.3),
                  ),
                ),
                child: TextField(
                  controller: _controller,
                  focusNode: _focusNode,
                  autofocus: true,
                  textInputAction: TextInputAction.search,
                  onChanged: _onQueryChanged,
                  onSubmitted: _submitSearch,
                  style: theme.textTheme.bodyMedium,
                  decoration: InputDecoration(
                    hintText: 'Search title, category, tag...',
                    hintStyle: theme.textTheme.bodyMedium?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant.withValues(alpha: 0.7),
                    ),
                    prefixIcon: Icon(
                      Icons.search_rounded,
                      size: AppSizes.iconMd - 2,
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                    suffixIcon: activeQuery.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear_rounded, size: AppSizes.iconSm + 2),
                            onPressed: _clearQuery,
                            tooltip: 'Clear',
                          )
                        : null,
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      vertical: AppSizes.p12,
                    ),
                  ),
                ),
              ),
            ),
            const SizedBox(width: AppSizes.p8),
          ],
        ),
      ),
      body: SafeArea(
        child: activeQuery.trim().isEmpty
            ? _buildRecentAndSuggestionsView(context, asyncRecentSearches)
            : Column(
                children: [
                  // Realtime Autocomplete Suggestions (when typing)
                  if (_focusNode.hasFocus && suggestions.isNotEmpty)
                    Container(
                      constraints: const BoxConstraints(maxHeight: 220.0),
                      color: theme.colorScheme.surface,
                      child: ListView.separated(
                        shrinkWrap: true,
                        itemCount: suggestions.length,
                        separatorBuilder: (context, index) => const Divider(height: 1.0),
                        itemBuilder: (context, index) {
                          final suggestion = suggestions[index];
                          return SuggestionTile(
                            suggestion: suggestion,
                            onTap: () => _selectQuery(suggestion.query),
                          );
                        },
                      ),
                    ),

                  // Results Grid
                  Expanded(
                    child: _buildSearchResultsGrid(
                        context, searchResults, activeQuery),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _buildRecentAndSuggestionsView(
    BuildContext context,
    AsyncValue<List<String>> asyncRecentSearches,
  ) {
    final theme = Theme.of(context);

    return SingleChildScrollView(
      physics: const BouncingScrollPhysics(),
      padding: const EdgeInsets.all(AppSizes.p16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Recent Searches Section
          asyncRecentSearches.when(
            data: (recentList) {
              if (recentList.isEmpty) return const SizedBox.shrink();

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Recent Searches',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      TextButton(
                        onPressed: () {
                          ref
                              .read(recentSearchesProvider.notifier)
                              .clearAll();
                        },
                        child: const Text('Clear All'),
                      ),
                    ],
                  ),
                  const SizedBox(height: AppSizes.p8),
                  Wrap(
                    spacing: AppSizes.p8,
                    runSpacing: AppSizes.p8,
                    children: recentList.map((query) {
                      return InputChip(
                        label: Text(query),
                        onPressed: () => _selectQuery(query),
                        onDeleted: () {
                          ref
                              .read(recentSearchesProvider.notifier)
                              .removeQuery(query);
                        },
                        deleteIcon: const Icon(Icons.close_rounded, size: 14.0),
                        backgroundColor: theme.colorScheme.surfaceContainerHighest
                            .withValues(alpha: 0.6),
                        labelStyle: theme.textTheme.labelMedium?.copyWith(
                          color: theme.colorScheme.onSurface,
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: AppSizes.p24),
                ],
              );
            },
            loading: () => const SizedBox.shrink(),
            error: (error, stack) => const SizedBox.shrink(),
          ),

          // Popular Search Suggestions Section
          Text(
            'Popular Suggestions',
            style: theme.textTheme.titleSmall?.copyWith(
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: AppSizes.p12),
          Wrap(
            spacing: AppSizes.p8,
            runSpacing: AppSizes.p8,
            children: _popularSuggestions.map((tag) {
              return ActionChip(
                avatar: const Icon(Icons.trending_up_rounded, size: 14.0),
                label: Text(tag[0].toUpperCase() + tag.substring(1)),
                onPressed: () => _selectQuery(tag),
                backgroundColor: theme.colorScheme.surfaceContainerHighest
                    .withValues(alpha: 0.5),
                labelStyle: theme.textTheme.labelMedium?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                  fontWeight: FontWeight.w500,
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchResultsGrid(
    BuildContext context,
    List<Wallpaper> searchResults,
    String activeQuery,
  ) {
    if (searchResults.isEmpty) {
      return EmptyStateView(
        icon: Icons.search_off_rounded,
        title: 'No Wallpapers Found',
        description:
            'No results matching "$activeQuery". Try searching for nature, cars, or abstract.',
        actionLabel: 'Clear Search',
        onAction: _clearQuery,
      );
    }

    final crossAxisCount = _calculateCrossAxisCount(context);

    return CustomScrollView(
      physics: const BouncingScrollPhysics(),
      slivers: [
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppSizes.p16,
              vertical: AppSizes.p12,
            ),
            child: Text(
              'Found ${searchResults.length} wallpapers for "$activeQuery"',
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppColors.disabled,
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ),
        ),
        SliverPadding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppSizes.p16,
            vertical: AppSizes.p8,
          ),
          sliver: SliverGrid(
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: crossAxisCount,
              mainAxisSpacing: AppSizes.p16,
              crossAxisSpacing: AppSizes.p16,
              childAspectRatio: 0.70,
            ),
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final wallpaper = searchResults[index];
                return WallpaperCard(
                  wallpaper: wallpaper,
                  onTap: () {
                    ref
                        .read(recentSearchesProvider.notifier)
                        .addQuery(activeQuery);
                    context.pushNamed(
                      RouteConstants.wallpaperDetailsName,
                      pathParameters: {'id': wallpaper.id},
                      extra: wallpaper,
                    );
                  },
                );
              },
              childCount: searchResults.length,
            ),
          ),
        ),
        const SliverToBoxAdapter(
          child: SizedBox(height: AppSizes.p24),
        ),
      ],
    );
  }

  int _calculateCrossAxisCount(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width > 900) return 4;
    if (width > 600) return 3;
    return 2;
  }
}
