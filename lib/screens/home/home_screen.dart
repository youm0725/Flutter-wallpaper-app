import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../models/wallpaper.dart';
import '../../providers/category_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/wallpaper_providers.dart';
import '../../widgets/category_chip.dart';
import '../../widgets/search_bar_widget.dart';
import '../../widgets/section_header.dart';
import '../../widgets/wallpaper_card.dart';

/// Production-quality Home Screen displaying wallpaper gallery, categories, and theme options.
class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  int _currentBottomNavIndex = 0;

  static const List<String> _categories = <String>[
    'All',
    'nature',
    'abstract',
    'amoled',
    'anime',
    'architecture',
    'cars',
    'gaming',
    'minimal',
    'space',
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final selectedCategory = ref.watch(selectedCategoryProvider);
    final asyncWallpapers = ref.watch(wallpapersProvider);

    return Scaffold(
      body: SafeArea(
        child: CustomScrollView(
          physics: const BouncingScrollPhysics(),
          slivers: [
            // Custom App Bar
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
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.3,
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
                    size: AppSizes.iconMd,
                  ),
                ),
                const SizedBox(width: AppSizes.p8),
              ],
            ),

            // Welcome Hero Section
            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(AppSizes.p16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Discover Wallpapers',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: AppSizes.p4),
                    Text(
                      'Handcrafted high-resolution wallpapers for your device.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // Search Bar (UI only)
            const SliverToBoxAdapter(
              child: Padding(
                padding: EdgeInsets.only(bottom: AppSizes.p16),
                child: SearchBarWidget(),
              ),
            ),

            // Categories Section Header
            const SliverToBoxAdapter(
              child: SectionHeader(
                title: 'Categories',
                subtitle: 'Filter by style',
              ),
            ),

            // Horizontal Categories List
            SliverToBoxAdapter(
              child: SizedBox(
                height: 40.0,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: AppSizes.p16),
                  itemCount: _categories.length,
                  itemBuilder: (context, index) {
                    final category = _categories[index];
                    final isSelected = selectedCategory.toLowerCase() == category.toLowerCase();
                    return CategoryChip(
                      label: category == 'All'
                          ? 'All'
                          : category[0].toUpperCase() + category.substring(1),
                      isSelected: isSelected,
                      onTap: () {
                        ref.read(selectedCategoryProvider.notifier).selectCategory(category);
                      },
                    );
                  },
                ),
              ),
            ),

            const SliverToBoxAdapter(
              child: SizedBox(height: AppSizes.p16),
            ),

            // Wallpaper Section Header
            const SliverToBoxAdapter(
              child: SectionHeader(
                title: 'Explore Gallery',
              ),
            ),

            // Wallpaper Grid content
            asyncWallpapers.when(
              data: (wallpapers) {
                final filteredWallpapers = selectedCategory == 'All'
                    ? wallpapers
                    : wallpapers
                        .where(
                          (w) => w.category.toLowerCase() == selectedCategory.toLowerCase(),
                        )
                        .toList();

                if (filteredWallpapers.isEmpty) {
                  return const SliverFillRemaining(
                    hasScrollBody: false,
                    child: Center(
                      child: Text(
                        'No wallpapers found in this category.',
                        style: TextStyle(
                          fontSize: 14.0,
                          color: AppColors.disabled,
                        ),
                      ),
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
                      crossAxisCount: _calculateCrossAxisCount(context),
                      mainAxisSpacing: AppSizes.p16,
                      crossAxisSpacing: AppSizes.p16,
                      childAspectRatio: 0.72,
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
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              ),
              error: (error, stack) => SliverFillRemaining(
                hasScrollBody: false,
                child: Center(
                  child: Text(
                    'Failed to load gallery: $error',
                    style: const TextStyle(color: Colors.red),
                  ),
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

  int _calculateCrossAxisCount(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    if (width > 900) return 4;
    if (width > 600) return 3;
    return 2;
  }

  void _onWallpaperTap(BuildContext context, Wallpaper wallpaper) {
    context.pushNamed(
      RouteConstants.wallpaperDetailsName,
      pathParameters: {'id': wallpaper.id},
    );
  }

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;

    setState(() {
      _currentBottomNavIndex = index;
    });

    if (index == 1) {
      context.pushNamed(RouteConstants.favoritesName);
    } else if (index == 2) {
      context.pushNamed(RouteConstants.settingsName);
    }
  }
}
