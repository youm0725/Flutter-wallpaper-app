import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../models/user_preferences.dart';
import '../../models/wallpaper.dart';
import '../../providers/category_provider.dart';
import '../../providers/preferences_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/wallpaper_providers.dart';
import '../../widgets/widgets.dart';

/// Clean, minimalist Home Screen featuring category filters & responsive wallpaper grid.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  static const int _currentBottomNavIndex = 0;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final selectedCategory = ref.watch(selectedCategoryProvider);
    final asyncWallpapers = ref.watch(wallpapersProvider);
    final prefs = ref.watch(userPreferencesNotifierProvider).value ?? const UserPreferences();

    final crossAxisCount = calculateGridCrossAxisCount(context, prefs.gridDensity);

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            // 1. App Bar
            SliverAppBar(
              floating: true,
              snap: true,
              elevation: 0,
              backgroundColor: theme.scaffoldBackgroundColor,
              title: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Wallpaper Gallery',
                    style: theme.textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w800,
                      letterSpacing: -0.4,
                    ),
                  ),
                  Text(
                    'Offline Collection',
                    style: theme.textTheme.labelSmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
              actions: [
                IconButton(
                  onPressed: () {
                    ref.read(themeModeProvider.notifier).toggleTheme();
                  },
                  tooltip: isDark ? 'Switch to Light Theme' : 'Switch to Dark Theme',
                  icon: Icon(
                    isDark ? Icons.light_mode_outlined : Icons.dark_mode_outlined,
                    size: AppSizes.iconMd - 2,
                  ),
                ),
                const SizedBox(width: AppSizes.p8),
              ],
            ),

            // 2. Categories Section Header & Horizontal Filter Chips
            SliverToBoxAdapter(
              child: SectionHeader(
                title: 'Categories',
                subtitle: 'Filter by style',
                trailing: TextButton(
                  onPressed: () => context.pushNamed(RouteConstants.categoriesName),
                  child: const Text('See All'),
                ),
              ),
            ),
            SliverToBoxAdapter(
              child: Builder(
                builder: (context) {
                  final categoriesList = ref.watch(categoriesProvider);
                  final categoryNames = <String>['All', ...categoriesList.map((c) => c.name)];

                  return SizedBox(
                    height: 44.0,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      physics: const BouncingScrollPhysics(),
                      padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
                      itemCount: categoryNames.length,
                      itemBuilder: (context, index) {
                        final category = categoryNames[index];
                        final isSelected =
                            selectedCategory.toLowerCase() == category.toLowerCase();
                        return CategoryChip(
                          label: category,
                          isSelected: isSelected,
                          onTap: () {
                            ref
                                .read(selectedCategoryProvider.notifier)
                                .selectCategory(category);
                          },
                        );
                      },
                    ),
                  );
                },
              ),
            ),

            const SliverToBoxAdapter(
              child: SizedBox(height: AppSizes.p16),
            ),

            // 3. Wallpaper Grid Section Header & Content
            const SliverToBoxAdapter(
              child: SectionHeader(
                title: 'Explore Gallery',
              ),
            ),
            asyncWallpapers.when(
              data: (wallpapers) {
                final filteredWallpapers = selectedCategory == 'All'
                    ? wallpapers
                    : wallpapers
                        .where(
                          (w) =>
                              w.category.toLowerCase() ==
                              selectedCategory.toLowerCase(),
                        )
                        .toList();

                if (filteredWallpapers.isEmpty) {
                  return const SliverFillRemaining(
                    hasScrollBody: false,
                    child: EmptyStateView(
                      title: 'No Wallpapers Found',
                      description: 'No wallpapers available in this category.',
                    ),
                  );
                }

                return SliverPadding(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppSizes.p16,
                    vertical: AppSizes.p8,
                  ),
                  sliver: SliverGrid(
                    gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: crossAxisCount,
                      mainAxisSpacing: AppSizes.p16,
                      crossAxisSpacing: AppSizes.p16,
                      childAspectRatio: 0.65,
                    ),
                    delegate: SliverChildBuilderDelegate(
                      (context, index) {
                        final wallpaper = filteredWallpapers[index];
                        return WallpaperCard(
                          wallpaper: wallpaper,
                          onTap: () => _onWallpaperTap(context, wallpaper),
                        );
                      },
                      childCount: filteredWallpapers.length,
                    ),
                  ),
                );
              },
              loading: () => const SliverFillRemaining(
                hasScrollBody: false,
                child: LoadingView(
                  message: 'Loading offline gallery...',
                ),
              ),
              error: (error, stack) => SliverFillRemaining(
                hasScrollBody: false,
                child: ErrorStateView(
                  message: error.toString(),
                  onRetry: () {
                    ref.invalidate(wallpapersProvider);
                  },
                ),
              ),
            ),

            const SliverToBoxAdapter(
              child: SizedBox(height: AppSizes.p24),
            ),
          ],
        ),
      ),

      // Bottom Navigation Bar
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentBottomNavIndex,
        onTap: (index) => _onBottomNavTapped(context, index),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite_outline_rounded),
            activeIcon: Icon(Icons.favorite_rounded),
            label: 'Favorites',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings_outlined),
            activeIcon: Icon(Icons.settings_rounded),
            label: 'Settings',
          ),
        ],
      ),
    );
  }

  void _onWallpaperTap(BuildContext context, Wallpaper wallpaper) {
    context.pushNamed(
      RouteConstants.wallpaperDetailsName,
      pathParameters: {'id': wallpaper.id},
      extra: wallpaper,
    );
  }

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;

    if (index == 1) {
      context.goNamed(RouteConstants.favoritesName);
    } else if (index == 2) {
      context.goNamed(RouteConstants.settingsName);
    }
  }
}
