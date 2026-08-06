import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_sizes.dart';
import '../../core/router/route_constants.dart';
import '../../providers/favorites_provider.dart';
import '../../providers/preferences_provider.dart';
import '../../providers/recently_viewed_provider.dart';
import '../../providers/theme_provider.dart';
import '../../providers/user_collection_provider.dart';
import '../../widgets/widgets.dart';

/// Production Settings Screen featuring appearance customization, grid density controls,
/// home feed section toggles, data management, and backup export foundation.
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final int _currentBottomNavIndex = 2;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final asyncPrefs = ref.watch(userPreferencesNotifierProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings & Preferences'),
      ),
      body: SafeArea(
        child: asyncPrefs.when(
          data: (prefs) => ListView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.symmetric(vertical: AppSizes.p12),
            children: [
              // 1. Appearance Section
              const SectionHeader(
                title: 'Appearance',
                subtitle: 'Theme and layout preferences',
              ),
              PreferenceTile(
                icon: isDark ? Icons.dark_mode_outlined : Icons.light_mode_outlined,
                title: 'Theme Mode',
                subtitle: isDark ? 'Dark Theme' : 'Light Theme',
                trailing: Switch.adaptive(
                  value: isDark,
                  onChanged: (_) {
                    ref.read(themeModeProvider.notifier).toggleTheme();
                  },
                ),
              ),
              PreferenceTile(
                icon: Icons.grid_view_rounded,
                title: 'Wallpaper Grid Layout',
                subtitle: 'Control thumbnail density',
                trailing: OptionSelector(
                  selectedDensity: prefs.gridDensity,
                  onSelected: (density) {
                    ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .setGridDensity(density);
                  },
                ),
              ),

              const Divider(height: AppSizes.p32),

              // 2. Home Feed Customization Section
              const SectionHeader(
                title: 'Home Feed Organization',
                subtitle: 'Toggle active discovery sections',
              ),
              PreferenceTile(
                icon: Icons.today_rounded,
                title: 'Wallpaper of the Day',
                subtitle: 'Show daily hero banner on home feed',
                trailing: Switch.adaptive(
                  value: prefs.showDailyWallpaper,
                  onChanged: (val) {
                    ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .toggleDailyWallpaper(val);
                  },
                ),
              ),
              PreferenceTile(
                icon: Icons.star_outline_rounded,
                title: "Editor's Picks",
                subtitle: 'Show featured wallpapers section',
                trailing: Switch.adaptive(
                  value: prefs.showFeaturedSection,
                  onChanged: (val) {
                    ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .toggleFeaturedSection(val);
                  },
                ),
              ),
              PreferenceTile(
                icon: Icons.history_rounded,
                title: 'Recently Viewed',
                subtitle: 'Show recent view history section',
                trailing: Switch.adaptive(
                  value: prefs.showRecentlyViewed,
                  onChanged: (val) {
                    ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .toggleRecentlyViewed(val);
                  },
                ),
              ),
              PreferenceTile(
                icon: Icons.collections_bookmark_outlined,
                title: 'Curated Collections',
                subtitle: 'Show themed collections on home feed',
                trailing: Switch.adaptive(
                  value: prefs.showCollectionsSection,
                  onChanged: (val) {
                    ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .toggleCollectionsSection(val);
                  },
                ),
              ),

              const Divider(height: AppSizes.p32),

              // 3. Local Data Management Section
              const SectionHeader(
                title: 'Data & Library Management',
                subtitle: 'Manage local offline storage',
              ),
              PreferenceTile(
                icon: Icons.folder_special_outlined,
                title: 'Personal Collections',
                subtitle: 'Manage custom user libraries',
                trailing: const Icon(Icons.chevron_right_rounded),
                onTap: () {
                  context.pushNamed(RouteConstants.userCollectionsName);
                },
              ),
              PreferenceTile(
                icon: Icons.delete_outline_rounded,
                title: 'Clear Recently Viewed History',
                subtitle: 'Reset wallpaper view history',
                onTap: () async {
                  final confirmed = await ConfirmationDialog.show(
                    context,
                    title: 'Clear History?',
                    message:
                        'Are you sure you want to clear your recently viewed wallpaper history?',
                    confirmLabel: 'Clear',
                    isDestructive: true,
                  );
                  if (confirmed == true) {
                    await ref
                        .read(recentlyViewedNotifierProvider.notifier)
                        .clearHistory();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Recently viewed history cleared'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    }
                  }
                },
              ),
              PreferenceTile(
                icon: Icons.heart_broken_outlined,
                title: 'Clear All Favorites',
                subtitle: 'Remove all saved favorite wallpapers',
                onTap: () async {
                  final confirmed = await ConfirmationDialog.show(
                    context,
                    title: 'Clear Favorites?',
                    message:
                        'Are you sure you want to remove all saved wallpapers from your favorites list?',
                    confirmLabel: 'Clear All',
                    isDestructive: true,
                  );
                  if (confirmed == true) {
                    final repo = ref.read(favoritesRepositoryProvider);
                    await repo.clearFavorites();
                    ref.invalidate(favoritesNotifierProvider);
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Favorites cleared'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    }
                  }
                },
              ),

              const Divider(height: AppSizes.p32),

              // 4. Backup Export / Import Foundation Section
              const SectionHeader(
                title: 'Backup & Restore',
                subtitle: 'Offline data backup foundation',
              ),
              PreferenceTile(
                icon: Icons.upload_file_outlined,
                title: 'Export Local Backup',
                subtitle: 'Generate offline JSON backup data',
                onTap: () async {
                  final favs =
                      ref.read(favoritesNotifierProvider).value?.toList() ?? [];
                  final userCols = ref
                          .read(userCollectionsNotifierProvider)
                          .value
                          ?.map((c) => c.toJson())
                          .toList() ??
                      [];
                  final currentPrefs = prefs.toJson();

                  final backupService = ref.read(backupServiceProvider);
                  final jsonStr = await backupService.exportBackupToJson(
                    favorites: favs,
                    userCollections: userCols,
                    preferences: currentPrefs,
                  );

                  if (context.mounted) {
                    showDialog<void>(
                      context: context,
                      builder: (context) => AlertDialog(
                        title: const Text('Backup Exported (JSON)'),
                        content: SingleChildScrollView(
                          child: SelectableText(
                            jsonStr,
                            style: const TextStyle(
                              fontFamily: 'monospace',
                              fontSize: 12.0,
                            ),
                          ),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: const Text('Close'),
                          ),
                        ],
                      ),
                    );
                  }
                },
              ),
              PreferenceTile(
                icon: Icons.restore_page_outlined,
                title: 'Reset All Preferences',
                subtitle: 'Restore default application settings',
                onTap: () async {
                  final confirmed = await ConfirmationDialog.show(
                    context,
                    title: 'Reset Preferences?',
                    message:
                        'Are you sure you want to reset all layout and view preferences to default?',
                    confirmLabel: 'Reset',
                  );
                  if (confirmed == true) {
                    await ref
                        .read(userPreferencesNotifierProvider.notifier)
                        .resetAll();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('Preferences reset to default'),
                          behavior: SnackBarBehavior.floating,
                        ),
                      );
                    }
                  }
                },
              ),

              const SizedBox(height: AppSizes.p32),
            ],
          ),
          loading: () => const LoadingView(message: 'Loading settings...'),
          error: (error, stack) => ErrorStateView(message: error.toString()),
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

  void _onBottomNavTapped(BuildContext context, int index) {
    if (index == _currentBottomNavIndex) return;

    if (index == 0) {
      context.goNamed(RouteConstants.homeName);
    } else if (index == 1) {
      context.goNamed(RouteConstants.favoritesName);
    }
  }
}
