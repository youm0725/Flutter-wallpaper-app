import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Provider holding the currently selected category filter.
final selectedCategoryProvider = StateProvider<String>((ref) => 'All');
