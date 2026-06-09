import { useRouter } from "expo-router";
import { Pressable, StyleSheet, Text, View } from "react-native";

import { useAuth } from "@/contexts/AuthContext";

export default function ProfileScreen() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  async function handleLogout() {
    await signOut();
    router.replace("/login");
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Telefone</Text>
      <Text style={styles.value}>{user?.phone ?? "—"}</Text>
      <Text style={styles.label}>Nome</Text>
      <Text style={styles.value}>{user?.name ?? "—"}</Text>
      <Pressable style={styles.button} onPress={handleLogout}>
        <Text style={styles.buttonText}>Sair</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24, backgroundColor: "#fafafa" },
  label: { fontSize: 13, color: "#666", marginTop: 16 },
  value: { fontSize: 18, fontWeight: "600" },
  button: {
    marginTop: 32,
    backgroundColor: "#dc2626",
    borderRadius: 8,
    padding: 14,
    alignItems: "center",
  },
  buttonText: { color: "#fff", fontWeight: "600" },
});
