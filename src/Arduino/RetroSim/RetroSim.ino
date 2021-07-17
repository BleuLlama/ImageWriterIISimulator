
void setup()
{
  Serial.begin( 9600 );

  while( !Serial );
}


void loop()
{
  Serial.println( "Phase A" );
  delay( 1000 );
  
  for( unsigned int i = 0x00 ; i <= 0xff ; i++ )
  {
    Serial.write( i );
  }
  Serial.println();

  Serial. println( "Phase B" );
  
  for( unsigned int i = 0x00 ; i <= 0xff ; i++ )
  {
    Serial.write( i );
    delay( 10 );
  }
  Serial.println();


  delay( 1000 );
}
