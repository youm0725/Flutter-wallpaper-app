import 'package:go_router/go_router.dart';
import '../../screens/details/wallpaper_details_screen.dart';
import '../../screens/favorites/favorites_screen.dart';
import '../../screens/home/home_screen.dart';
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
      path: RouteConstants.wallpaperDetailsPath,
      name: RouteConstants.wallpaperDetailsName,
      builder: (context, state) {
        final id = state.pathParameters['id'] ?? '';
        return WallpaperDetailsScreen(wallpaperId: id);
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
