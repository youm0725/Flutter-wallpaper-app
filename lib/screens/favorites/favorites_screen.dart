import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../models/wallpaper.dart';
import '../../providers/favorites_provider.dart';
import '../../widgets/widgets.dart';

/// Production-ready Favorites Screen displaying saved offline wallpapers.
class FavoritesScreen extends ConsumerStatefulWidget {
  const FavoritesScreen({super.key});

  @override
  ConsumerState<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends ConsumerState<FavoritesScreen> {
  final int _currentBottomNavIndex = 1;

  @override
  Widget build(BuildContext context) {
    final favoriteWallpapers = ref.watch(favoriteWallpapersProvider);
    final crossAxisCount = _calculateCrossAxisCount(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Favorites'),
      ),
      body: SafeArea(
        child: favoriteWallpapers.isEmpty
            ? const EmptyStateView(
                icon: Icons.favorite_border_rounded,
                title: 'No Favorites Yet',
                description:
                    'Save wallpapers you love by tapping the heart icon and find them here anytime.',
              )
            : CustomScrollView(
                physics: const BouncingScrollPhysics(),
                slivers: [
                  SliverToBoxAdapter(
                    child: SectionHeader(
                      title: 'Saved Wallpapers',
                      subtitle: '${favoriteWallpapers.length} items in your offline collection',
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
                          final wallpaper = favoriteWallpapers[index];
                          return WallpaperCard(
                            wallpaper: wallpaper,
                            onTap: () => _onWallpaperTap(context, wallpaper),
                          );
                        },
                        childCount: favoriteWallpapers.length,
                      ),
                    ),
                  ),
                  const SliverToBoxAdapter(
                    child: SizedBox(height: AppSizes.p24),
                  ),
                ],
              ),
      ),
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
      extra: wallpaper,
    );
  }

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;

    if (index == 0) {
      context.goNamed(RouteConstants.homeName);
    } else if (index == 2) {
      context.goNamed(RouteConstants.settingsName);
    }
  }
}
