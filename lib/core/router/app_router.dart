import 'package:go_router/go_router.dart';
import '../../screens/home/home_screen.dart';
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
  ],
);
