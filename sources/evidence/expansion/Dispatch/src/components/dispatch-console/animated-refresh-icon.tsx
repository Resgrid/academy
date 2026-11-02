import { RefreshCw } from 'lucide-react-native';
import { useColorScheme } from 'nativewind';
import React, { useEffect } from 'react';
import Animated, { cancelAnimation, Easing, useAnimatedStyle, useSharedValue, withRepeat, withTiming } from 'react-native-reanimated';

interface AnimatedRefreshIconProps {
  isLoading: boolean;
  size?: number;
}

export const AnimatedRefreshIcon: React.FC<AnimatedRefreshIconProps> = ({ isLoading, size = 14 }) => {
  const { colorScheme } = useColorScheme();
  const rotation = useSharedValue(0);

  useEffect(() => {
    if (isLoading) {
      rotation.value = withRepeat(
        withTiming(360, {
          duration: 1000,
          easing: Easing.linear,
        }),
        -1, // Infinite repeats
        false // Don't reverse
      );
    } else {
      cancelAnimation(rotation);
      rotation.value = withTiming(0, { duration: 200 });
    }

    return () => {
      cancelAnimation(rotation);
    };
  }, [isLoading, rotation]);

  const animatedStyle = useAnimatedStyle(() => {
    return {
      transform: [{ rotate: `${rotation.value}deg` }],
    };
  });

  const iconColor = colorScheme === 'dark' ? '#9ca3af' : '#6b7280';

  return (
    <Animated.View style={animatedStyle}>
      <RefreshCw size={size} color={iconColor} />
    </Animated.View>
  );
};
