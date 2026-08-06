import 'package:flutter/material.dart';
import '../core/constants/app_sizes.dart';

/// A segmented three-way theme selector for System, Light, and Dark modes.
/// Matches the aesthetic of [OptionSelector] used for grid density.
class ThemeSelector extends StatelessWidget {
  final ThemeMode selectedMode;
  final ValueChanged<ThemeMode> onSelected;

  const ThemeSelector({
    super.key,
    required this.selectedMode,
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
        children: _options.map((option) {
          final isSelected = option.mode == selectedMode;
          return GestureDetector(
            onTap: () => onSelected(option.mode),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(
                horizontal: AppSizes.p8,
                vertical: AppSizes.p6,
              ),
              decoration: BoxDecoration(
                color: isSelected
                    ? theme.colorScheme.primary
                    : Colors.transparent,
                borderRadius:
                    BorderRadius.circular(AppSizes.radiusSm - 2),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    option.icon,
                    size: 14.0,
                    color: isSelected
                        ? theme.colorScheme.onPrimary
                        : theme.colorScheme.onSurfaceVariant,
                  ),
                  const SizedBox(width: AppSizes.p4),
                  Text(
                    option.label,
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight:
                          isSelected ? FontWeight.w700 : FontWeight.w500,
                      color: isSelected
                          ? theme.colorScheme.onPrimary
                          : theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _ThemeOption {
  final ThemeMode mode;
  final IconData icon;
  final String label;
  const _ThemeOption(this.mode, this.icon, this.label);
}

const _options = [
  _ThemeOption(ThemeMode.system, Icons.brightness_auto_rounded, 'Auto'),
  _ThemeOption(ThemeMode.light, Icons.light_mode_outlined, 'Light'),
  _ThemeOption(ThemeMode.dark, Icons.dark_mode_outlined, 'Dark'),
];
