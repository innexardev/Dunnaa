import { SymbolView } from "expo-symbols";
import { Tabs } from "expo-router";

import Colors from "@/constants/Colors";
import { useColorScheme } from "@/components/useColorScheme";

export default function TabLayout() {
  const colorScheme = useColorScheme();

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? "light"].tint,
        headerShown: true,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: "Início",
          tabBarIcon: ({ color }) => (
            <SymbolView name={{ ios: "magnifyingglass", android: "search", web: "search" }} tintColor={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen
        name="appointments"
        options={{
          title: "Agenda",
          tabBarIcon: ({ color }) => (
            <SymbolView name={{ ios: "calendar", android: "calendar_today", web: "calendar_today" }} tintColor={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen
        name="queue"
        options={{
          title: "Fila",
          tabBarIcon: ({ color }) => (
            <SymbolView name={{ ios: "person.3", android: "groups", web: "groups" }} tintColor={color} size={24} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Perfil",
          tabBarIcon: ({ color }) => (
            <SymbolView name={{ ios: "person.circle", android: "person", web: "person" }} tintColor={color} size={24} />
          ),
        }}
      />
    </Tabs>
  );
}
