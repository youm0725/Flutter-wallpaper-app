import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Notifier managing the currently selected category filter.
class SelectedCategoryNotifier extends Notifier<String> {
  @override
  String build() {
    return 'All';
  }

  void selectCategory(String category) {
    state = category;
  }
}

/// Riverpod provider for the currently selected category.
final selectedCategoryProvider =
    NotifierProvider<SelectedCategoryNotifier, String>(
  SelectedCategoryNotifier.new,
);
