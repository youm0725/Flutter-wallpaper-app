import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';
import '../models/user_preferences.dart';

/// Segmented option selector for choosing wallpaper grid density.
class OptionSelector extends StatelessWidget {
  final GridDensity selectedDensity;
  final ValueChanged<GridDensity> onSelected;

  const OptionSelector({
    super.key,
    required this.selectedDensity,
    required this.onSelected,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      padding: const EdgeInsets.all(AppSizes.p4),
      decoration: BoxDecoration(
        color: theme.colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
        borderRadius: BorderRadius.circular(AppSizes.radiusSm),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: GridDensity.values.map((density) {
          final isSelected = density == selectedDensity;
          return GestureDetector(
            onTap: () => onSelected(density),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(
                horizontal: AppSizes.p12,
                vertical: AppSizes.p6,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? theme.colorScheme.primary
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(AppSizes.radiusSm - 2),
              ),
              child: Text(
                _getLabel(density),
                style: theme.textTheme.labelSmall?.copyWith(
                  fontWeight: isSelected ? FontWeight.w700 : FontWeight.w500,
                  color: isSelected
                      ? theme.colorScheme.onPrimary
                      : theme.colorScheme.onSurfaceVariant,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  String _getLabel(GridDensity density) {
    switch (density) {
      case GridDensity.compact:
        return 'Compact';
      case GridDensity.comfortable:
        return 'Comfortable';
      case GridDensity.large:
        return 'Large';
    }
  }
}
