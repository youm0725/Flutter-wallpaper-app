import 'package:go_router/go_router.dart';
import '../../models/wallpaper.dart';
import '../../screens/categories/categories_screen.dart';
import '../../screens/collections/user_collections_screen.dart';
import '../../screens/details/wallpaper_details_screen.dart';
import '../../screens/favorites/favorites_screen.dart';
import '../../screens/home/home_screen.dart';
import '../../screens/search/search_screen.dart';
import '../../screens/settings/settings_screen.dart';
import '../../screens/splash/splash_screen.dart';
import 'route_constants.dart';

/// Application routing configuration using GoRouter.
final GoRouter appRouter = GoRouter(
  initialLocation: RouteConstants.splashPath,
  routes: [
    GoRoute(
      path: RouteConstants.splashPath,
      name: RouteConstants.splashName,
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: RouteConstants.homePath,
      name: RouteConstants.homeName,
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: RouteConstants.categoriesPath,
      name: RouteConstants.categoriesName,
      builder: (context, state) => const CategoriesScreen(),
    ),
    GoRoute(
      path: RouteConstants.userCollectionsPath,
      name: RouteConstants.userCollectionsName,
      builder: (context, state) => const UserCollectionsScreen(),
    ),
    GoRoute(
      path: RouteConstants.searchPath,
      name: RouteConstants.searchName,
      builder: (context, state) => const SearchScreen(),
    ),
    GoRoute(
      path: RouteConstants.wallpaperDetailsPath,
      name: RouteConstants.wallpaperDetailsName,
      builder: (context, state) {
        final id = state.pathParameters['id'] ?? '';
        final wallpaper = state.extra is Wallpaper ? state.extra as Wallpaper : null;
        return WallpaperDetailsScreen(
          wallpaperId: id,
          wallpaper: wallpaper,
        );
      },
    ),
    GoRoute(
      path: RouteConstants.favoritesPath,
      name: RouteConstants.favoritesName,
      builder: (context, state) => const FavoritesScreen(),
    ),
    GoRoute(
      path: RouteConstants.settingsPath,
      name: RouteConstants.settingsName,
      builder: (context, state) => const SettingsScreen(),
    ),
  ],
);
