<!-- File is no longer used. Trying to reuse this as a way to set filepath
in the app. Still having a few difficulties -->
<template>
  <v-container fluid fill-height>
    <v-layout column justify-space-around>
      <input type="text" :value="getLogFile"/>
      <button @click="saveFile">Save</button>
      <v-flex xs1>Streamdecker integration is not yet available due to issues in how Twitch treats extensions. For now we recommend <b><i>not</i></b> running the Streamdecker component while we work with Twitch on a fix.</v-flex>
    </v-layout>
  </v-container>
</template>

<script>

export default {
  data: function () {
    return {
      typedPath: ''
    }
  },
  computed: {
    getLogFile: function () {
      return this.$store.state.arenaFilePath
    },
    saveFile: function () {

    }
  }
}
</script>

<style scoped>
.flex {
  padding: 10vw;
}
</style>
